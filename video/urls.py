from django.urls import path
from . import views

app_name = 'video'

urlpatterns = [
    path('upload/', views.upload_video, name='upload'),
    path('list/', views.video_list, name='list'),
    path('<int:pk>/', views.video_detail, name='detail'),
]
