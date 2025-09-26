import os
import shutil
import uuid
import subprocess
import json
from io import BytesIO
from minio import Minio
from celery import shared_task
from .models import Video, AudioTrack
from .utils import upload_video_to_minio
import boto3
import langcodes

# MinIO Client Configuration
client = Minio( 
    'localhost:9000',  # MinIO endpoint
    access_key='admin',  # Access key
    secret_key='admin123',  # Secret key
    secure=False  # False for HTTP, True for HTTPS
)

def get_full_language_name(code):
    """Return the full language name for a given code."""
    language = langcodes.Language.make(code)
    return language.display_name()

def generate_uuid():
    """Generate a unique UUID string."""
    return str(uuid.uuid4())

def create_download_folder(video_uuid):
    """Create a local folder to download video/audio files."""
    folder_path = os.path.join('downloads', video_uuid)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def create_output_folder(base_path, video_uuid):
    """Create a local folder for transcoded video/audio files."""
    folder_path = os.path.join(base_path, video_uuid)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def get_file_from_minio(bucket_name, file_key, download_path):
    """Download the file from MinIO to a local file."""
    response = client.get_object(bucket_name, file_key)
    with open(download_path, 'wb') as f:
        f.write(response.read())

def analyze_audio_streams(input_file):
    """Analyze video using ffprobe and return list of audio streams."""
    ffprobe_command = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', input_file
    ]
    result = subprocess.run(ffprobe_command, capture_output=True, text=True)
    ffprobe_output = json.loads(result.stdout)
    audio_streams = [s for s in ffprobe_output['streams'] if s['codec_type'] == 'audio']
    return audio_streams

def encode_video_only(input_file, output_folder):
    """Encode video-only HLS stream."""
    video_hls_command = [
        'ffmpeg', '-i', input_file, '-map', '0:v', '-an', '-c:v', 'libx264', '-b:v', '2M',
        '-maxrate:v', '2M', '-bufsize:v', '4M', '-f', 'hls', '-hls_time', '10', '-hls_list_size', '0',
        '-hls_segment_filename', f"{output_folder}/vsegment_%d.ts",
        f"{output_folder}/video_playlist.m3u8"
    ]
    subprocess.run(video_hls_command, check=True)

def encode_audio_streams(input_file, output_folder, audio_streams, video_obj):
    """
    Encode each audio stream as a separate HLS playlist,
    create AudioTrack objects in DB, and return list of (language, playlist_name).
    """
    audio_playlists = []

    for audio_stream in audio_streams:
        print('ap are ',audio_stream)
        stream_index = audio_stream['index']
        language = audio_stream.get('tags', {}).get('language', f'audio{stream_index}')
        audio_playlist_name = f"audio_{language}_playlist.m3u8"
        audio_playlists.append((language, audio_playlist_name))

        # 1. Encode audio HLS segments
        audio_hls_command = [
            'ffmpeg', '-i', input_file, '-map', f"0:{stream_index}", '-vn', '-c:a', 'aac', '-b:a', '128k',
            '-f', 'hls', '-hls_time', '10', '-hls_list_size', '0',
            '-hls_segment_filename', f"{output_folder}/asegment_{language}_%d.ts",
            f"{output_folder}/{audio_playlist_name}"
        ]
        subprocess.run(audio_hls_command, check=True)

        # 2. Create AudioTrack object in DB
        AudioTrack.objects.create(
            video=video_obj,
            language=language,
            transcoded_playlist=f"{video_obj.transcoding_uuid}/{audio_playlist_name}"
        )

    return audio_playlists

def generate_master_playlist(output_folder, audio_playlists):
    """Generate master.m3u8 linking video and audio tracks, with the first audio track as default."""
    master_playlist_path = os.path.join(output_folder, 'master.m3u8')

    with open(master_playlist_path, 'w') as f:
        f.write('#EXTM3U\n')
        f.write('#EXT-X-VERSION:7\n')

        # Add audio tracks
        for idx, (language, playlist) in enumerate(audio_playlists):
            full_language_name = get_full_language_name(language)  # Get full language name
            # Set the first audio track to be the default
            default_value = 'YES' if idx == 0 else 'NO'
            
            f.write(
                f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="{full_language_name}",LANGUAGE="{language}",DEFAULT={default_value},AUTOSELECT=YES,URI="{playlist}"\n'
            )

        # Add video stream with AUDIO group
        f.write('#EXT-X-STREAM-INF:BANDWIDTH=2000000,AUDIO="audio"\n')
        f.write('video_playlist.m3u8\n')



@shared_task
def transcode_video(video_id):
    """Main Celery task: transcode video and audio tracks, generate master playlist, and upload to MinIO."""
    video = Video.objects.get(id=video_id)

    # 1. Assign UUID and create output folder
    video_uuid = generate_uuid()
    video.transcoding_uuid = video_uuid
    video.status = 'in_progress'  # Update status to "in_progress"
    video.save()

    # 2. Create a folder to download the video
    download_folder = create_download_folder(video_uuid)
    input_path = os.path.join(download_folder, f'{video_uuid}.mp4')  # Local download path

    # 3. Download video from MinIO to local disk
    video_file_key = video.video_file.name  # Get the file key (path in MinIO)
    get_file_from_minio('videos', video_file_key, input_path)  # Download to local

    # 4. Create output folder for transcoding
    output_folder = create_output_folder('transcoded_video', video_uuid)

    try:
        # 5. Analyze audio streams
        audio_streams = analyze_audio_streams(input_path)

        # 6. Encode video-only HLS
        encode_video_only(input_path, output_folder)

        # 7. Encode each audio track
        audio_playlists = encode_audio_streams(input_path, output_folder, audio_streams, video)

        # 8. Generate master playlist
        generate_master_playlist(output_folder, audio_playlists)

        subprocess.run(['mc', 'cp', '-r', output_folder, f'myminio/videos/transcoded_videos'], check=True)

        # 9. Upload all files to MinIO

        # 10. Update video model with transcoded details and status
        video.transcoded_video = f"{video_uuid}/video_playlist.m3u8"
        video.master_playlist = f"{video_uuid}/master.m3u8"
        video.status = 'completed'  # Update status to "completed"
        video.save()

        # 11. Cleanup: Remove the local download and output folders after successful upload

    except Exception as e:
        # In case of any error during transcoding
        video.status = 'failed'  # Set status to "failed"
        video.save()
        raise e
