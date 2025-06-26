from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.external_api.user_s_selected_book import UsersSelectedBook
from apps.external_api.keyword_flow import KeywordRecommendationFlow
from apps.external_api.bestseller import BestsellerRecommendation
from apps.external_api.age_group import AgeGroupRecommendationFlow
import os
import json

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
def get_recommendation_api(request):
    isbn13 = request.data.get("isbn13")
    recommendation_type = request.data.get("recommendation_type", "reader")

    if not isbn13:
        return JsonResponse({"error": "Missing ISBN"}, status=400)

    recommender = UsersSelectedBook(auth_key=os.environ.get("DATA4LIBRARY_API_KEY"))
    books = recommender.get_similar_books(isbn13, recommendation_type=recommendation_type)
    return JsonResponse({"books": books})



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