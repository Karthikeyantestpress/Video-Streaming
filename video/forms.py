from django import forms
from .models import Video
from .utils import create_uuid


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_file']

    def save(self, commit=True):
        # Create a UUID before saving
        if not self.instance.transcoding_uuid:
            self.instance.transcoding_uuid = create_uuid()
        return super().save(commit=commit)


# New form for uploading audio to an existing video
from .models import AudioTrack


from .utils import get_language_display_name

# Define a set of common language codes (ISO 639-1)
COMMON_LANGUAGE_CODES = [
    'en', 'es', 'fr', 'de', 'hi', 'zh', 'ja', 'ru', 'ar', 'pt', 'it', 'ko', 'ta', 'te', 'ml', 'bn', 'ur', 'tr', 'vi', 'id'
]

class AudioUploadForm(forms.ModelForm):
    language = forms.ChoiceField(
        choices=[(code, get_language_display_name(code)) for code in COMMON_LANGUAGE_CODES],
        required=True,
        help_text="Select the language for this audio track."
    )

    class Meta:
        model = AudioTrack
        fields = ['audio_file', 'language']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['audio_file'].required = True