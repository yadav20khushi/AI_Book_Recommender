

# Create your views here.
from django.shortcuts import render, redirect
from apps.external_api.keyword_flow import KeywordRecommendationFlow
import os

def keyword_page(request):
    api_key = os.environ.get("DATA4LIBRARY_API_KEY")
    recommender = KeywordRecommendationFlow(auth_key=api_key)
    keywords = recommender.get_monthly_keywords()
    return render(request, 'keyword_page.html', {'keywords': keywords})


def age_group_page(request):
    return render(request, 'ageGroup_page.html')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Optional: only if CSRF becomes an issue
def books_by_keyword(request):
    if request.method == "POST":
        selected_keyword = request.POST.get("keyword")
        # Pass selected keyword to logic → fetch books
        recommender = KeywordRecommendationFlow(auth_key=os.environ.get("DATA4LIBRARY_API_KEY"))
        books = recommender.get_books_by_keyword(selected_keyword)
        return render(request, 'bookList_page.html', {'books': books, 'keyword': selected_keyword})


def book_list_by_keyword(request):
    if request.method == 'POST':
        selected_kw = request.POST.get('keyword')
        books = KeywordRecommendationFlow.get_books_by_keyword(selected_kw)
        return render(request, 'bookList_page.html', {'books': books})
    return redirect('keyword_page')


def bestseller_page(request):
    return render(request, 'bestseller_page.html')  # Optional page