import os
import subprocess
import shutil
from celery import shared_task
from .models import Video, AudioTrack
from .utils import (
    get_language_display_name,
    create_uuid,
    make_download_directory,
    make_transcoded_directory,
    download_file_from_minio,
    get_audio_streams_from_video
)

def encode_video_to_hls(input_file, output_folder):
    video_hls_command = [
        'ffmpeg', '-i', input_file, '-map', '0:v', '-an', '-c:v', 'libx264', '-b:v', '2M',
        '-maxrate:v', '2M', '-bufsize:v', '4M', '-f', 'hls', '-hls_time', '10', '-hls_list_size', '0',
        '-hls_segment_filename', f"{output_folder}/vsegment_%d.ts",
        f"{output_folder}/video_playlist.m3u8"
    ]
    subprocess.run(video_hls_command, check=True)

def encode_audio_streams_to_hls(input_file, output_folder, audio_streams, video_obj):
    audio_playlists = []

    for audio_stream in audio_streams:
        stream_index = audio_stream['index']
        language = audio_stream.get('tags', {}).get('language', f'audio{stream_index}')
        audio_playlist_name = f"audio_{language}_playlist.m3u8"
        audio_playlists.append((language, audio_playlist_name))

        audio_hls_command = [
            'ffmpeg', '-i', input_file, '-map', f"0:{stream_index}", '-vn', '-c:a', 'aac', '-b:a', '128k',
            '-f', 'hls', '-hls_time', '10', '-hls_list_size', '0',
            '-hls_segment_filename', f"{output_folder}/asegment_{language}_%d.ts",
            f"{output_folder}/{audio_playlist_name}"
        ]
        subprocess.run(audio_hls_command, check=True)

        AudioTrack.objects.create(
            video=video_obj,
            language=language,
            transcoded_playlist=f"{video_obj.transcoding_uuid}/{audio_playlist_name}"
        )

    return audio_playlists

def create_master_hls_playlist(output_folder, audio_playlists):
    master_playlist_path = os.path.join(output_folder, 'master.m3u8')

    with open(master_playlist_path, 'w') as f:
        f.write('#EXTM3U\n')
        f.write('#EXT-X-VERSION:7\n')
        for idx, (language, playlist) in enumerate(audio_playlists):
            full_language_name = get_language_display_name(language)
            default_value = 'YES' if idx == 0 else 'NO'
            f.write(f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="{full_language_name}",LANGUAGE="{language}",DEFAULT={default_value},AUTOSELECT=YES,URI="{playlist}"\n')
        f.write('#EXT-X-STREAM-INF:BANDWIDTH=2000000,AUDIO="audio"\n')
        f.write('video_playlist.m3u8\n')



@shared_task
def transcode_video(video_id):
    video = Video.objects.get(id=video_id)
    video.status = 'in_progress'
    video.save()
    download_folder = make_download_directory(video_uuid)
    input_path = os.path.join(download_folder, f'{video_uuid}.mp4')
    video_file_key = video.video_file.name
    download_file_from_minio('videos', video_file_key, input_path)
    output_folder = make_transcoded_directory('transcoded_video', video_uuid)
    try:
        audio_streams = get_audio_streams_from_video(input_path)
        encode_video_to_hls(input_path, output_folder)
        audio_playlists = encode_audio_streams_to_hls(input_path, output_folder, audio_streams, video)
        create_master_hls_playlist(output_folder, audio_playlists)
        subprocess.run(['mc', 'cp', '-r', output_folder, f'myminio/videos/transcoded_videos'], check=True)
        video.transcoded_video = f"{video_uuid}/video_playlist.m3u8"
        video.master_playlist = f"{video_uuid}/master.m3u8"
        video.status = 'completed'
        video.save()
        
    except Exception as e:
        video.status = 'failed'
        video.save()
        raise e
    
    shutil.rmtree(download_folder)
    shutil.rmtree(output_folder)
