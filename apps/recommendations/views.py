from django.shortcuts import render
from apps.recommendations.recommendation import ClovaBookChatHandler
from apps.external_api.user_s_selected_book import UsersSelectedBook
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json

import os
# def selected_book(request):
@api_view(["POST"])
def selected_book_api(request):
    if request.method == "POST":
        isbn13 = request.POST.get("isbn13")
        if isbn13:
            recommender = UsersSelectedBook(auth_key=os.environ.get("DATA4LIBRARY_API_KEY"))
            description = recommender.get_description(isbn13)
            username = request.user.username


            handler = ClovaBookChatHandler(username=username)
            result = handler.start_chat(description)  # using method from the class

    if "session" in result:
        request.session["chat_history"] = result["session"]

    return JsonResponse({
        "clova_response": result["response"],
        "chat_session": result["session"]
    })


# def followup_question(request):
#     if request.method == "POST":
#         user_input = request.POST.get("user_input")
#         username = request.user.username if request.user.is_authenticated else "guest"

#         # Retrieve previous session history from Django session
#         session_messages = request.session.get("chat_history", [])

#         # Handle follow-up with Clova
#         handler = ClovaBookChatHandler(username=username)
#         result = handler.followup_chat(session_messages, user_input)

#         # Update session history with new exchange
#         request.session["chat_history"] = result["session"]

#         return JsonResponse({
#             "clova_response": result["response"]
#         })

#     return JsonResponse({"error": "Invalid request method"}, status=400)



@api_view(["POST"])
def followup_question_api(request):
    try:
        session = request.data.get('session_messages', [])

        if not session:
            return JsonResponse({'error': 'Missing session messages'}, status=400)

        user_input = session[-1]["content"]

        handler = ClovaBookChatHandler(username=request.user.username)
        result = handler.followup_chat(session, user_input)

        return JsonResponse({
            'clova_response': result["response"],
            'session': result["session"]
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)