from apps.recommendations.models import ChatHistory
from django.contrib.auth.models import User


def chat_history_context(request):
    chat_history = []
    username = request.user.username if request.user.is_authenticated else request.session.get("username")

    if username:
        chat_history = ChatHistory.objects.filter(
            user_history__user__username=username
        ).order_by('-timestamp')

    return {"chat_history": chat_history}
