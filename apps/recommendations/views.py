# Create your views here.

from django.shortcuts import render, redirect
from apps.recommendations.recommendation import call_clova
from apps.external_api.users_selected_book import UsersSelectedBook
from apps.books.models import Book

def selected_book(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")

        description = UsersSelectedBook.get_description(isbn13)
        clova_response = call_clova(description) #also pass username later on

        return render(request, "clovaChat_page.html", {
            "clova_response": clova_response
        })
