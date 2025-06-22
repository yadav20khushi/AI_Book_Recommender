from django.shortcuts import render, redirect
from apps.recommendations.recommendation import ClovaBookChatHandler
from apps.external_api.users_selected_book import UsersSelectedBook
from django.http import JsonResponse
from django.http import HttpResponse
import os

def selected_book(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")
        if isbn13:
            recommender = UsersSelectedBook(auth_key=os.environ.get("DATA4LIBRARY_API_KEY"))
            description = recommender.get_description(isbn13)
            username = request.user.username if request.user.is_authenticated else "guest"

            handler = ClovaBookChatHandler(username=username)
            result = handler.start_chat(description)  # using method from the class

            # Store full session history in Django session (for follow-up)
            request.session["chat_history"] = result["session"]

            return render(request, "clovaChat_page.html", {
                "clova_response": result["response"],
                "chat_session": result["session"],
                "isbn13": isbn13
            })


def followup_question(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        username = request.user.username if request.user.is_authenticated else "guest"

        # Retrieve previous session history from Django session
        session_messages = request.session.get("chat_history", [])

        # Handle follow-up with Clova
        handler = ClovaBookChatHandler(username=username)
        result = handler.followup_chat(session_messages, user_input)

        # Update session history with new exchange
        request.session["chat_history"] = result["session"]

        return JsonResponse({
            "clova_response": result["response"]
        })

    return JsonResponse({"error": "Invalid request method"}, status=400)


def handle_recommendation_type(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")
        rec_type = request.POST.get("recommendation_type", "reader")

        if not isbn13:
            return HttpResponse("Missing ISBN. Please try again.", status=400)

        api_key = os.environ.get("DATA4LIBRARY_API_KEY")
        recommender = UsersSelectedBook(auth_key=api_key)

        books = recommender.get_similar_books(isbn13, recommendation_type=rec_type)
        #print(books)
        return render(request, "bookList_page.html", {"books": books})

    return HttpResponse("Invalid request method.", status=405)


def check_availability_view(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")
        lib_code = request.POST.get("lib_code", "127058")  # Default for now

        if not isbn13:
            return HttpResponse("책 정보가 제공되지 않았습니다.", status=400)

        api_key = os.environ.get("DATA4LIBRARY_API_KEY")
        recommender = UsersSelectedBook(auth_key=api_key)
        message = recommender.check_availability(isbn13, lib_code)
        return HttpResponse(message)

    return HttpResponse("잘못된 요청입니다.", status=400)


