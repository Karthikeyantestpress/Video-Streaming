# 🎥 Django Video Streaming Platform

A complete **Django-based Video Streaming Platform** that supports **HLS transcoding**, **multi-language audio tracks**, **background processing with Celery**, and **S3-compatible storage** using **MinIO**.

This project allows users to:
- Upload videos (MP4 format).
- Transcode videos into HLS format (`.m3u8` playlists + `.ts` segments).
- Automatically extract and manage multiple audio tracks.
- Upload additional language-specific audio tracks.
- Store and serve files from **MinIO** (S3-compatible).
- Process tasks asynchronously using **Celery** with **Redis** broker.

---

## 🚀 Features

- ✅ Video upload via web form.
- ✅ Asynchronous transcoding with Celery.
- ✅ FFmpeg-based HLS conversion.
- ✅ Multi-language audio support.
- ✅ Master playlist generation (`master.m3u8`).
- ✅ MinIO (S3-compatible) storage.
- ✅ Track status and progress.
- ✅ Readable language names with `langcodes`.

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

## 📁 Folder Structure

