from django.shortcuts import render

# Create your views here.

def clova_chat_page(request):
    return render(request, 'clovaChat_page.html')
