from django.db import models
from .utils import get_language_display_name

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')  # Original uploaded video
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # New fields for transcoding
    transcoding_uuid = models.UUIDField(null=True, blank=True, editable=False)  # Unique UUID for transcoded folder
    transcoded_video = models.CharField(
        max_length=500, 
        null=True, 
        blank=True,
        help_text="Local path or reference folder of transcoded video and audio files"
    )
    master_playlist = models.CharField(
        max_length=500, 
        null=True, 
        blank=True,
        help_text="Path or MinIO key for master.m3u8"
    )
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Status of the video transcoding process"
    )

    def __str__(self):
        return self.title


class AudioTrack(models.Model):
    video = models.ForeignKey(Video, related_name='audio_tracks', on_delete=models.CASCADE)
    language = models.CharField(max_length=100)
    audio_file = models.FileField(upload_to='audio_tracks/')  # Original uploaded audio (if separate)
    is_default = models.BooleanField(default=False)

    # New fields for transcoded audio
    transcoded_playlist = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Path or MinIO key for this audio track's HLS playlist (audio_XX_playlist.m3u8)"
    )

    def __str__(self):
        return f'{self.language} - {self.video.title}'
   
    @property
    def display_language(self):
        return get_language_display_name(self.language)
