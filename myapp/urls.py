from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

# myapp/urls.py
from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat_page, name='chat_page'),
    path('book/<str:isbn>/', views.book_detail, name='book_detail'),
    path('api/chat/', views.unified_chat_api, name='unified_chat_api'),
    path('api/video_summary/', views.unified_video_summary_api, name='unified_video_summary_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)