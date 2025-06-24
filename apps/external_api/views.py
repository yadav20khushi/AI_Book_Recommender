# from django.shortcuts import render, redirect
# from apps.external_api.keyword_flow import KeywordRecommendationFlow
# from apps.external_api.bestseller import BestsellerRecommendation
# from apps.external_api.age_group import AgeGroupRecommendationFlow
# from django.views.decorators.csrf import csrf_exempt
# import os

# def keyword_page(request):
#     api_key = os.environ.get("DATA4LIBRARY_API_KEY")
#     recommender = KeywordRecommendationFlow(auth_key=api_key)
#     keywords = recommender.get_monthly_keywords()
#     return render(request, 'keyword_page.html', {'keywords': keywords})

# @csrf_exempt  # Optional: only if CSRF becomes an issue
# def books_by_keyword(request):
#     if request.method == "POST":
#         selected_keyword = request.POST.get("keyword")
#         if selected_keyword:
#             recommender = KeywordRecommendationFlow(auth_key=os.environ.get("DATA4LIBRARY_API_KEY"))
#             books = recommender.get_books_by_keyword(selected_keyword)
#             #print("Books returned:", books)
#             return render(request, 'bookList_page.html', {'books': books, 'keyword': selected_keyword})
#     return redirect('keyword_page')

# def age_group_page(request):
#     return render(request, 'ageGroup_page.html')

# @csrf_exempt
# def book_list_by_agegroup(request):
#     if request.method == "POST":
#         selected_group = request.POST.get("age_group", "overall")  # fallback to "overall"
#         recommender = AgeGroupRecommendationFlow(auth_key=os.environ.get("DATA4LIBRARY_API_KEY"))
#         books = recommender.get_books_by_agegroup(selected_group)
#         return render(request, 'bookList_page.html', {'books': books})
#     return redirect('age_group_page')  # fallback

# def bestseller_books(request):
#     auth_key = os.environ.get("DATA4LIBRARY_API_KEY")
#     recommender = BestsellerRecommendation(auth_key)
#     books = recommender.get_bestseller_books()
#     return render(request, 'bookList_page.html', {'books': books})



from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.external_api.user_s_selected_book import UsersSelectedBook
from apps.external_api.keyword_flow import KeywordRecommendationFlow
from apps.external_api.bestseller import BestsellerRecommendation
from apps.external_api.age_group import AgeGroupRecommendationFlow
import os

@api_view(["GET"])
def keyword_api(request):
    api_key = os.environ.get("DATA4LIBRARY_API_KEY")
    if not api_key:
        return Response({"error": "Missing DATA4LIBRARY_API_KEY"}, status=500)

    recommender = KeywordRecommendationFlow(auth_key=api_key)

    try:
        keywords = recommender.get_monthly_keywords()
        if not keywords:
            return Response({"keywords": [], "error": "No keywords found."}, status=200)
        return Response({"keywords": keywords})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(["POST"])
def books_by_keyword_api(request):
    keyword = request.data.get("keyword")
    if not keyword:
        return Response({"error": "No keyword provided."}, status=400)
    
    recommender = KeywordRecommendationFlow(auth_key=os.environ.get("DATA4LIBRARY_API_KEY"))
    books = recommender.get_books_by_keyword(keyword)
    return Response({"books": books})

@api_view(["POST"])
def get_description_api(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")
        data = UsersSelectedBook(auth_key=os.environ.get("DATA4LIBRARY_API_KEY")).get_description(isbn13)
        return JsonResponse({"data": data})


@api_view(["POST"])
def get_similar_books_api(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")
        recommendation_type = request.POST.get("type", "reader")
        data = UsersSelectedBook(auth_key=os.environ.get("DATA4LIBRARY_API_KEY")).get_similar_books(isbn13, recommendation_type)
        return JsonResponse({"books": data})
    
@api_view(["POST"])
def get_advanced_books_api(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")
        recommendation_type = request.POST.get("type", "mania")
        data = UsersSelectedBook(auth_key=os.environ.get("DATA4LIBRARY_API_KEY")).get_similar_books(isbn13, recommendation_type)
        return JsonResponse({"books": data})


@api_view(["POST"])
def check_availability_api(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")
        lib_code = request.POST.get("lib_code", "111100")  # default or test libCode
        status = UsersSelectedBook(auth_key=os.environ.get("DATA4LIBRARY_API_KEY")).check_availability(isbn13, lib_code)
        return JsonResponse({"availability": status})
    
@api_view(["POST"])
def book_metadata_api(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")
        book_info = UsersSelectedBook(auth_key=os.environ.get("DATA4LIBRARY_API_KEY")).get_description(isbn13)

        # Return just the basic book info (title, author, cover)
        if book_info:
            selected = book_info[0]
            return JsonResponse({
                "title": selected.get("title", "N/A"),
                "author": selected.get("authors", "N/A"),
                "cover": selected.get("cover", "")
            })
        else:
            return JsonResponse({"error": "Book not found"}, status=404)
        
import json
@api_view(["POST"])
def book_list_by_agegroup_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            selected_group = data.get("age_group", "overall")
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        recommender = AgeGroupRecommendationFlow(auth_key=os.environ.get("DATA4LIBRARY_API_KEY"))
        books = recommender.get_books_by_agegroup(selected_group)

        return JsonResponse({"books": books})
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

@api_view(["GET"])
def bestseller_books_api(request):
    auth_key = os.environ.get("DATA4LIBRARY_API_KEY")
    recommender = BestsellerRecommendation(auth_key)
    books = recommender.get_bestseller_books()
    return JsonResponse({"books": books})