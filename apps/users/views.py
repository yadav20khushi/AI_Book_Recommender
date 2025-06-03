from django.shortcuts import render

# Create your views here.
def home_page(request):
    return render(request, 'home_page.html')
def login_view(request):
    return render(request, "login.html")

def signup_view(request):
    return render(request, "signup.html")

def returning_user_view(request):
    return render(request, "returningUser_page.html")
