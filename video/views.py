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

def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    return render(request, 'video/video_detail.html', {'video': video})
