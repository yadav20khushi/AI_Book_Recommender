from django.shortcuts import render, redirect
from apps.recommendations.models import UserHistory
from apps.external_api.personal_recommendations import ReturningUserRecommendationFlow
from django.utils import timezone

# Create your views here.
def home_page_view(request):
    if not request.session.get("username"):
        return redirect("signup")
    return render(request, "home_page.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = UserHistory.objects.get(username=username)
            if user.password == password:  # (I'll hash later in MySQL)
                request.session["username"] = username
                return redirect("returning_user")  # go to their saved books
            else:
                return render(request, "login.html", {"error": "비밀번호가 틀렸습니다."})
        except UserHistory.DoesNotExist:
            return render(request, "login.html", {"error": "사용자가 존재하지 않습니다."})

    return render(request, "login.html")



def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if user exists
        if UserHistory.objects.filter(username=username).exists():
            # Redirect to login if user already signed up
            return redirect("login")  # URL name for your login page

        # If new user → save to DB
        UserHistory.objects.create(username=username, password=password)
        request.session["username"] = username
        return redirect("home_page")  # now logged in

    return render(request, "signup.html")

from django.shortcuts import redirect

def signout_view(request):
    request.session.flush()  # Clears all session data
    return redirect("login")  # Or "login" if you prefer


def returning_user(request):
    username = request.session.get("username")

    if not username:
        return redirect("login")

    # Use your backend logic to get recommended books
    recommender = ReturningUserRecommendationFlow(username=username)
    recommended_books = recommender.get_avid_reader_recommendations()

    return render(request, "returningUser_page.html", {
        "books": recommended_books,
        "username": username
    })

