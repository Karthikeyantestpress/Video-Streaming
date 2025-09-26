from minio import Minio

client = Minio(
    'localhost:9000',
    access_key='admin',
    secret_key='admin123',
    secure=False
)

def upload_video_to_minio(video_file, file_name):
    client.fput_object('videos', file_name, video_file)
