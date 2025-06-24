# apps/external_api/urls.py

from django.urls import path
from . import views


urlpatterns = [
    # path('keyword/', views.keyword_page, name='keyword_page'),
    # path('age-group/', views.age_group_page, name='age_group_page'),
    # path('age-group/books/', views.book_list_by_agegroup, name='book_list_by_agegroup'),
    # path('keyword/books/', views.books_by_keyword, name='book_list_by_keyword'),
    # path('books/by-keyword/', views.books_by_keyword, name='book_list_by_keyword'),
    # path('bestsellers/', views.bestseller_books, name='bestseller_books'),



    path("keywords/", views.keyword_api, name="monthly_keywords_api"),
    path("books_by_keyword/", views.books_by_keyword_api, name="books_by_keyword_api"),
    path('book_metadata/', views.book_metadata_api, name='book_metadata_api'),
    path('book_description/', views.get_description_api, name='book_description_api'),
    path('similar_books/', views.get_similar_books_api, name='similar_books_api'),
    path('advanced_books/', views.get_advanced_books_api, name='advanced_books_api'),
    path('check_availability/', views.check_availability_api, name='check_availability_api'),
    path('books_by_agegroup/', views.book_list_by_agegroup_api, name='books_by_agegroup_api'),
    path("bestsellers/", views.bestseller_books_api, name="bestseller_books_api"),
]
