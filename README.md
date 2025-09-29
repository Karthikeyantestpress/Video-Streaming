````markdown
# 🎥 Django Video Streaming Platform

A complete **Django-based Video Streaming Platform** that supports **HLS transcoding**, **multi-language audio tracks**, **background processing with Celery**, and **S3-compatible storage** using **MinIO**.

This project allows users to:
- Upload videos (MP4 format)
- Transcode videos into HLS format (`.m3u8` playlists + `.ts` segments)
- Automatically extract and manage multiple audio tracks
- Upload additional language-specific audio tracks
- Store and serve files from **MinIO** (S3-compatible)
- Process tasks asynchronously using **Celery** with **Redis** broker

---

## 🚀 Features

- ✅ Video upload via web form  
- ✅ Asynchronous transcoding with Celery  
- ✅ FFmpeg-based HLS conversion  
- ✅ Multi-language audio support  
- ✅ Master playlist generation (`master.m3u8`)  
- ✅ MinIO (S3-compatible) storage  
- ✅ Track status and progress  
- ✅ Readable language names with `langcodes`

---

## 🧱 Tech Stack

| Component | Description |
|-----------|-------------|
| **Framework** | Django 5.2.6 |
| **Async Tasks** | Celery 5.5.3 |
| **Broker** | Redis |
| **Storage** | MinIO |
| **Encoding** | FFmpeg |
| **ORM** | Django ORM (SQLite by default) |

---

## ⚙️ Setup Instructions

Follow these steps to set up and run the project locally:

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/Karthikeyantestpress/Video-Streaming.git
   cd Video-Streaming
````

2. **Create and Activate Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate       # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg**

   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ffmpeg -version
   ffprobe -version
   ```

5. **Start Redis (for Celery)**

   ```bash
   redis-server
   ```

   Keep this running in a separate terminal.

6. **Start MinIO (S3-Compatible Storage)**

   ```bash
   minio server /data --console-address ":9001"
   ```

   Open [http://localhost:9001](http://localhost:9001)
   Login credentials:

   ```
   Username: admin
   Password: admin123
   ```

   Create a bucket named **videos**.

7. **Apply Database Migrations**

   ```bash
   python manage.py migrate
   ```

8. **Create Superuser (Optional)**

   ```bash
   python manage.py createsuperuser
   ```

9. **Start Celery Worker (in a new terminal)**

   ```bash
   source venv/bin/activate
   celery -A video_streaming worker -l info
   ```

10. **Start Django Server**

    ```bash
    python manage.py runserver
    ```

Now open the app in your browser:

* App: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Admin: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

```
```
