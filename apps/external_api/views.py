

# Create your views here.
from django.shortcuts import render

def keyword_page(request):
    return render(request, 'keyword_page.html')

def age_group_page(request):
    return render(request, 'ageGroup_page.html')

def book_list_page(request):
    return render(request, 'bookList_page.html')

def bestseller_page(request):
    return render(request, 'bestseller_page.html')  # Optional page