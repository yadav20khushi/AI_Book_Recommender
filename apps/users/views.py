# from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate, login, logout
# from apps.recommendations.models import UserHistory
# from apps.external_api.personal_recommendations import ReturningUserRecommendationFlow


# def home_page_view(request):
#     if not request.user.is_authenticated:
#         return redirect("login")
#     return render(request, "home_page.html")

# @csrf_exempt
# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             return redirect("returning_user")
#         else:
#             return render(request, "login.html", {"error": "잘못된 로그인 정보입니다."})

#     return render(request, "login.html")


# def signup_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         if User.objects.filter(username=username).exists():
#             return redirect("login")

#         user = User.objects.create_user(username=username, password=password)
#         login(request, user)
#         return redirect("home_page")

#     return render(request, "signup.html")


# def signout_view(request):
#     logout(request)
#     return redirect("login")


# def returning_user(request):
#     if not request.user.is_authenticated:
#         return redirect("login")

#     recommender = ReturningUserRecommendationFlow(username=request.user.username)
#     recommended_books = recommender.get_avid_reader_recommendations()

#     return render(request, "returningUser_page.html", {
#         "books": recommended_books,
#         "username": request.user.username
#     })


from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from apps.external_api.personal_recommendations import ReturningUserRecommendationFlow

@csrf_exempt
@api_view(["POST"])
def api_signup(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=status.HTTP_409_CONFLICT)

    user = User.objects.create_user(username=username, password=password)
    login(request, user)
    return Response({"message": "Signup successful", "username": user.username}, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(["POST"])
def api_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({"message": "Login successful", "username": user.username})
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@csrf_exempt
@api_view(["POST"])
def api_logout(request):
    logout(request)
    return Response({"message": "Logged out successfully"})

@csrf_exempt
@api_view(["GET"])
def check_auth(request):
    if request.user.is_authenticated:
        return Response({"authenticated": True, "username": request.user.username})
    else:
        return Response({"authenticated": False})
    
from django.views.decorators.http import require_GET

@csrf_exempt
def returning_user_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    recommender = ReturningUserRecommendationFlow(username=request.user.username)
    isbns = recommender.get_user_isbns()
    print("Collected ISBNs from UserHistory:", isbns)
    recommender.get_avid_reader_recommendations()
    recommended_books = recommender.get_avid_reader_recommendations()

    return JsonResponse({
        "books": recommended_books,
        "username": request.user.username
    })