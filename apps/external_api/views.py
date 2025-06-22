from django.shortcuts import render, redirect
from apps.external_api.keyword_flow import KeywordRecommendationFlow
from apps.external_api.bestseller import BestsellerRecommendation
from apps.external_api.age_group import AgeGroupRecommendationFlow
from django.views.decorators.csrf import csrf_exempt
import os

def keyword_page(request):
    api_key = os.environ.get("DATA4LIBRARY_API_KEY")
    recommender = KeywordRecommendationFlow(auth_key=api_key)
    keywords = recommender.get_monthly_keywords()
    return render(request, 'keyword_page.html', {'keywords': keywords})

@csrf_exempt  # Optional: only if CSRF becomes an issue
def books_by_keyword(request):
    if request.method == "POST":
        selected_keyword = request.POST.get("keyword")
        if selected_keyword:
            recommender = KeywordRecommendationFlow(auth_key=os.environ.get("DATA4LIBRARY_API_KEY"))
            books = recommender.get_books_by_keyword(selected_keyword)
            #print("Books returned:", books)
            return render(request, 'bookList_page.html', {'books': books, 'keyword': selected_keyword})
    return redirect('keyword_page')

def age_group_page(request):
    return render(request, 'ageGroup_page.html')

@csrf_exempt
def book_list_by_agegroup(request):
    if request.method == "POST":
        selected_group = request.POST.get("age_group", "overall")  # fallback to "overall"
        recommender = AgeGroupRecommendationFlow(auth_key=os.environ.get("DATA4LIBRARY_API_KEY"))
        books = recommender.get_books_by_agegroup(selected_group)
        return render(request, 'bookList_page.html', {'books': books})
    return redirect('age_group_page')  # fallback

def bestseller_books(request):
    auth_key = os.environ.get("DATA4LIBRARY_API_KEY")
    recommender = BestsellerRecommendation(auth_key)
    books = recommender.get_bestseller_books()
    return render(request, 'bookList_page.html', {'books': books})
