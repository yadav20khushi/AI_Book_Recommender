from django.shortcuts import render
from apps.recommendations.recommendation import ClovaBookChatHandler
from apps.external_api.users_selected_book import UsersSelectedBook
from django.http import JsonResponse


def selected_book(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")
        print("Selected ISBN:", isbn13)

        description = UsersSelectedBook().get_description(isbn13)
        print(description)
        username = request.user.username if request.user.is_authenticated else "guest"

        handler = ClovaBookChatHandler(username=username)
        result = handler.start_chat(description)  # using method from the class

        # Store full session history in Django session (for follow-up)
        request.session["chat_history"] = result["session"]

        return render(request, "clovaChat_page.html", {
            "clova_response": result["response"],
            "chat_session": result["session"],
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
