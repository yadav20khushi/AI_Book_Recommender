from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from apps.recommendations.models import ChatHistory
from apps.recommendations.models import UserHistory
from django.contrib.auth.models import User
from apps.external_api.personal_recommendations import ReturningUserRecommendationFlow


def home_page_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "home_page.html")

def load_chat_view(request):
    if request.method == "POST":
        chat_id = request.POST.get("chat_id")
        chat = get_object_or_404(ChatHistory, id=chat_id)

        return render(request, "clovaChat_page.html", {
            "messages": chat.messages,
            "chat_id": chat.id,
            "book_title": chat.user_history.book.title,
        })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("returning_user")
        else:
            return render(request, "login.html", {"error": "잘못된 로그인 정보입니다."})

    return render(request, "login.html")


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return redirect("login")

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("home_page")

    return render(request, "signup.html")


def signout_view(request):
    logout(request)
    return redirect("login")


def returning_user(request):
    if not request.user.is_authenticated:
        return redirect("login")

    recommender = ReturningUserRecommendationFlow(username=request.user.username)
    recommended_books = recommender.get_avid_reader_recommendations()

    return render(request, "returningUser_page.html", {
        "books": recommended_books,
        "username": request.user.username
    })
