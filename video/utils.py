import os
import uuid
import subprocess
import json
import langcodes
from langcodes import standardize_tag
from minio import Minio

client = Minio(
    'localhost:9000',
    access_key='admin',
    secret_key='admin123',
    secure=False
)

def get_language_display_name(language_code):
    language_code = standardize_tag(language_code)
    language = langcodes.Language.make(language_code)
    return language.display_name()

def create_uuid():
    return str(uuid.uuid4())

def make_download_directory(video_uuid):
    folder_path = os.path.join('downloads', video_uuid)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def make_transcoded_directory(base_path, video_uuid):
    folder_path = os.path.join(base_path, video_uuid)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def download_file_from_minio(bucket_name, file_key, download_path):
    response = client.get_object(bucket_name, file_key)
    with open(download_path, 'wb') as f:
        f.write(response.read())

def get_audio_streams_from_video(input_file):
    ffprobe_command = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', input_file
    ]
    result = subprocess.run(ffprobe_command, capture_output=True, text=True)
    ffprobe_output = json.loads(result.stdout)
    audio_streams = [s for s in ffprobe_output['streams'] if s['codec_type'] == 'audio']
    return audio_streams



