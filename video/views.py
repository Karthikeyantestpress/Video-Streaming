from django.shortcuts import render, redirect, get_object_or_404
from .forms import VideoUploadForm
from .models import Video
from .tasks import transcode_video

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            # Trigger video transcoding via Celery
            transcode_video.delay(video.id)
            return redirect('video:list')
    else:
        form = VideoUploadForm()
    
    return render(request, 'video/upload_video.html', {'form': form})

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video/video_list.html', {'videos': videos})


from .forms import AudioUploadForm
from .models import AudioTrack
from .tasks import transcode_audio_for_video

def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    audio_form = AudioUploadForm()
    audio_upload_success = False

    if request.method == 'POST' and 'audio_upload' in request.POST:
        audio_form = AudioUploadForm(request.POST, request.FILES)
        if audio_form.is_valid():
            audio_track = audio_form.save(commit=False)
            audio_track.video = video
            audio_track.is_user_uploaded = True
            audio_track.save()
            # Trigger audio-only transcoding task
            transcode_audio_for_video.delay(audio_track.id)
            audio_upload_success = True

    return render(request, 'video/video_detail.html', {
        'video': video,
        'audio_form': audio_form,
        'audio_upload_success': audio_upload_success,
    })
