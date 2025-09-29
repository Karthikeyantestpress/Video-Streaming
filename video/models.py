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

    progress = models.PositiveSmallIntegerField(default=0, help_text="Transcoding progress percentage (0-100)")

    def __str__(self):
        return self.title


class AudioTrack(models.Model):
    video = models.ForeignKey(Video, related_name='audio_tracks', on_delete=models.CASCADE)
    language = models.CharField(max_length=100)
    # This field is now used for user-uploaded audio files (mp3, aac, etc.)
    audio_file = models.FileField(upload_to='audio_tracks/', null=True, blank=True, help_text="User-uploaded audio file (mp3, aac, etc.)")
    is_default = models.BooleanField(default=False)

    # New fields for transcoded audio
    transcoded_playlist = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Path or MinIO key for this audio track's HLS playlist (audio_XX_playlist.m3u8)"
    )

    # Field to distinguish if this audio was uploaded by user or extracted from video
    is_user_uploaded = models.BooleanField(default=False, help_text="True if this audio was uploaded by user, False if extracted from video.")



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
        help_text="Status of the audio transcoding process"
    )
    progress = models.PositiveSmallIntegerField(default=0, help_text="Audio transcoding progress percentage (0-100)")

    def __str__(self):
        return f'{self.language} - {self.video.title}'
   
    @property
    def display_language(self):
        return get_language_display_name(self.language)
