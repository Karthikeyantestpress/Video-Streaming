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