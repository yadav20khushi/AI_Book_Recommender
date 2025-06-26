from django.urls import path
from . import views

# myapp/urls.py
from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/search/', views.search_books, name='search_books'),
    path('api/popular_books_by_location/', views.popular_books_by_location, name='popular_books_by_location'),
    path('api/book_introduction/', views.book_introduction_api, name='book_introduction_api'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('chat/', views.chat_page, name='chat_page'),
    path('book/<str:isbn>/', views.book_detail, name='book_detail'),
    path('api/get_location_data/', views.get_location_data, name='get_location_data'),
    path('api/get_genre_data/', views.get_genre_data, name='get_genre_data'),
    path('api/generate_book_summary_video/', views.generate_book_summary_video_api, name='generate_book_summary_video_api'),
]

