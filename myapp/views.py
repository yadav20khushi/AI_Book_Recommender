# myapp/views.py
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from .services import LibraryAPIService, process_user_message
import os
from .video_summary import generate_book_summary_video

def home(request):
    """Home page view"""
    return render(request, 'myapp/home.html')

@csrf_exempt
def search_books(request):
    """API endpoint for book search using Library API with bullet point formatting"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            
            # Use the main process_user_message function that formats with bullet points
            response_text = process_user_message(query)
            
            # Parse the response to extract book data if needed
            books = []
            if "BOOKLIST_JSON:" in response_text:
                try:
                    json_part = response_text.split("BOOKLIST_JSON:")[1].strip()
                    json_lines = json_part.split('\n')
                    for line in json_lines:
                        if line.strip():
                            book_data = json.loads(line.strip())
                            books.append(book_data)
                except:
                    pass
            
            return JsonResponse({
                'success': True,
                'response': response_text,
                'books': books,
                'total': len(books)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def popular_books_by_location(request):
    """API endpoint for location-based popular books"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            location_code = data.get('location_code', None)
            dtl_kdc_code = data.get('dtl_kdc_code', None)
            page_no = data.get('page_no', 1)
            page_size = data.get('page_size', 20)
            
            service = LibraryAPIService(
                hyperclova_api_key=getattr(settings, 'HYPERCLOVA_API_KEY', None),
                library_api_key=getattr(settings, 'LIBRARY_API_KEY', None)
            )
            
            books = service.get_popular_books_by_location(
                location_code, page_no, page_size, dtl_kdc_code
            )
            
            # Format books with bullet points
            if books:
                book_lines = []
                for b in books:
                    book_lines.append(f"- **{b['bookname']}** by {b['authors']}\n  ◦ 출판: {b['publisher']} ({b['publication_year']})\n  ◦ 대출 횟수: {b['loan_count']}회")
                
                formatted_response = f"해당 지역의 인기 도서 목록입니다:\n\n" + '\n\n'.join(book_lines)
            else:
                formatted_response = "해당 지역의 인기 도서를 찾을 수 없습니다."
            
            return JsonResponse({
                'success': True,
                'response': formatted_response,
                'books': books,
                'total': len(books)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def book_detail(request, isbn):
    """Book detail view"""
    context = {
        'isbn': isbn
    }
    return render(request, 'myapp/book_detail.html', context)

@csrf_exempt
def chat_api(request):
    """API endpoint for chat messages - uses Library API only"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Always use process_user_message for Library API responses with bullet formatting
            response = process_user_message(user_message)
            
            return JsonResponse({
                'success': True,
                'response': response
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'POST only'})

@csrf_exempt
def book_introduction_api(request):
    """API endpoint for generating book introductions"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            book = data.get('book', {})
            
            service = LibraryAPIService(
                hyperclova_api_key=getattr(settings, 'HYPERCLOVA_API_KEY', None),
                library_api_key=getattr(settings, 'LIBRARY_API_KEY', None)
            )
            
            introduction = service.generate_book_introduction(book)
            
            return JsonResponse({
                'success': True,
                'introduction': introduction
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'POST only'})

def chat_page(request):
    """Renders the chat UI page"""
    # Load location data for the frontend
    service = LibraryAPIService()
    context = {
        'location_data': service.location_data,
        'dtl_kdc_dict': service.dtl_kdc_dict
    }
    return render(request, 'myapp/chat.html', context)

def get_location_data(request):
    """API endpoint to get location data"""
    service = LibraryAPIService()
    return JsonResponse({
        'success': True,
        'location_data': service.location_data
    })

def get_genre_data(request):
    """API endpoint to get genre/KDC data"""
    service = LibraryAPIService()
    return JsonResponse({
        'success': True,
        'dtl_kdc_dict': service.dtl_kdc_dict
    })

@csrf_exempt
def generate_book_summary_video_api(request):
    """API endpoint to generate a book summary video and return its URL"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            book = data.get('book', {})
            api_key = getattr(settings, 'HYPERCLOVA_API_KEY', None)
            video_path = generate_book_summary_video(book, api_key)
            if video_path and os.path.exists(video_path):
                # Serve the video file from a static-like endpoint
                video_url = f"/media/generated_videos/{os.path.basename(video_path)}"
                # Move/copy the file to a media directory if needed
                media_dir = os.path.join(settings.MEDIA_ROOT, 'generated_videos')
                os.makedirs(media_dir, exist_ok=True)
                final_path = os.path.join(media_dir, os.path.basename(video_path))
                if video_path != final_path:
                    import shutil
                    shutil.copy(video_path, final_path)
                return JsonResponse({'success': True, 'video_url': video_url})
            else:
                return JsonResponse({'success': False, 'error': 'Video generation failed.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'POST only'})