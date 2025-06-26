# myapp/services.py
import requests
import json
from datetime import datetime
from difflib import SequenceMatcher
import re
from django.conf import settings
import string
import unicodedata
import os

class LibraryAPIService:
    def __init__(self, hyperclova_api_key=None, library_api_key=None):
        self.hyperclova_api_key = hyperclova_api_key or getattr(settings, 'HYPERCLOVA_API_KEY', None)
        self.library_api_key = library_api_key or getattr(settings, 'LIBRARY_API_KEY', None)
        self.dtl_kdc_dict = self.load_dtl_kdc_json()
        self.location_data = self.load_location_data()
    
    def load_dtl_kdc_json(self):
        """Load the detailed KDC JSON file"""
        try:
            base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            json_path = os.path.join(base_dir, 'myapp', 'dtl_kdc.json')
            with open(json_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[DEBUG] dtl_kdc.json file not found at {json_path}!")
            return {}
        except Exception as e:
            print(f"[DEBUG] Error loading dtl_kdc.json: {e}")
            return {}
    
    def load_location_data(self):
        """Load location data from dtl_region.json"""
        try:
            base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            json_path = os.path.join(base_dir, 'myapp', 'dtl_region.json')
            with open(json_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[DEBUG] dtl_region.json file not found at {json_path}!")
            return []
        except Exception as e:
            print(f"[DEBUG] Error loading dtl_region.json: {e}")
            return []
    
    def call_hyperclova_api(self, messages, api_key=None):
        """Helper function to call HyperCLOVA API with correct headers"""
        api_key = api_key or self.hyperclova_api_key
        if not api_key:
            return None
            
        try:
            endpoint = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": messages,
                "maxTokens": 1024,
                "temperature": 0.7,
                "topP": 0.8,
            }
            
            response = requests.post(endpoint, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result['result']['message']['content']
            else:
                return None
        except Exception:
            return None
    
    def extract_keywords_with_hyperclova(self, user_input, api_key=None):
        """Extract and detect if the user is asking for books by a specific author or a genre (robust natural language support)"""
        api_key = api_key or self.hyperclova_api_key
        if not api_key:
            return self.detect_author_or_genre_fallback(user_input)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Enhanced multi-language author detection prompt with more natural language examples
        author_detection_prompt = f"""
사용자 입력 분석: "{user_input}"

다음 기준으로 요청 유형을 정확히 판단해주세요:

**작가 검색 패턴:**
- 한국 작가: "박경리", "김영하", "무라카미 하루키", "황석영 작품", "이문열 소설"
- 외국 작가: "Stephen King", "J.K. Rowling", "Agatha Christie", "셰익스피어", "헤밍웨이"
- 작가 관련 표현: "~의 작품", "~가 쓴", "~저자", "~작가의 책", "books by ~", "recommend me books by ~", "show me books by ~", "books written by ~", "author ~", "작가 ~", "저자 ~", "책 by ~"

**장르/주제 검색 패턴:**
- 문학 장르: "로맨스", "추리소설", "판타지", "SF", "호러", "스릴러"
- 주제 분야: "역사책", "철학서", "과학도서", "경제학", "자기계발"
- 일반적 표현: "~에 관한 책", "~분야", "~관련 도서"

**판단 규칙:**
1. 사람의 이름(성+이름 또는 단일명)이 포함 → 작가 검색
2. 문학 장르나 학문 분야명만 포함 → 장르 검색
3. 애매한 경우 문맥으로 판단

응답 형식:
- 작가 검색: "AUTHOR:작가이름"
- 장르 검색: "GENRE"

예시:
"무라카미 하루키 신작" → AUTHOR:무라카미 하루키
"미스터리 소설 추천해줘" → GENRE
"스티븐 킹" → AUTHOR:스티븐 킹
"철학 관련 서적" → GENRE
"해리포터 작가 책" → AUTHOR:J.K. Rowling
"recommend me books by Stephen King" → AUTHOR:Stephen King
"show me books by Agatha Christie" → AUTHOR:Agatha Christie
"books written by 헤밍웨이" → AUTHOR:헤밍웨이
"author 무라카미 하루키" → AUTHOR:무라카미 하루키
"""
        
        data_detection = {
            "messages": [
                {
                    "role": "system",
                    "content": "당신은 도서 검색 요청을 정확히 분석하는 전문가입니다. 사용자가 특정 작가의 책을 찾는지, 아니면 특정 장르나 주제의 책을 찾는지 명확하게 구분해야 합니다. 작가 이름이 포함되면 작가 검색, 장르나 주제만 언급되면 장르 검색으로 판단합니다. 반드시 아래 응답 형식만 사용하세요."
                },
                {
                    "role": "user", 
                    "content": author_detection_prompt
                }
            ],
            "maxTokens": 150,
            "temperature": 0.1,
            "topP": 0.3,
        }
        
        try:
            response = requests.post(
                "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
                headers=headers,
                json=data_detection,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                detection_result = result['result']['message']['content'].strip()
                
                # Parse the response more robustly
                if "AUTHOR:" in detection_result:
                    author_name = detection_result.split("AUTHOR:")[-1].strip()
                    author_name = author_name.replace('"', '').replace("'", '').strip()
                    if author_name:
                        return ("AUTHOR", author_name)
                elif "GENRE" in detection_result:
                    return ("GENRE", user_input)
                
                # If response format is unexpected, try fallback
                return self.enhanced_fallback_extraction(user_input)
            else:
                return self.enhanced_fallback_extraction(user_input)
                
        except Exception:
            return self.enhanced_fallback_extraction(user_input)

    def enhanced_fallback_extraction(self, user_input):
        """Improved fallback method to detect if input is author name or genre without API"""
        normalized_input = user_input.lower().strip()
        
        # Author-related regex patterns (English & Korean)
        author_patterns = [
            r'books by ([\w\s\.\-가-힣]+)',         # books by Stephen King
            r'by author ([\w\s\.\-가-힣]+)',        # by author J.K. Rowling
            r'author ([\w\s\.\-가-힣]+)',           # author 무라카미 하루키
            r'작가[ ]*([\w\s\.\-가-힣]+)',           # 작가 무라카미 하루키
            r'저자[ ]*([\w\s\.\-가-힣]+)',           # 저자 김영하
            r'([\w\s\.\-가-힣]+)의 작품',            # 김영하의 작품
            r'([\w\s\.\-가-힣]+)가 쓴',              # 김영하가 쓴
            r'([\w\s\.\-가-힣]+) 작가의 책',          # 김영하 작가의 책
            r'books written by ([\w\s\.\-가-힣]+)', # books written by Hemingway
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                author_name = match.group(1).strip()
                # Remove trailing words like '책', '소설', etc.
                author_name = re.sub(r'(책|소설|작품|author|저자|작가)$', '', author_name, flags=re.IGNORECASE).strip()
                if author_name:
                    return ("AUTHOR", author_name)
        
        # Fallback to original logic if no pattern matched
        return self.detect_author_or_genre_fallback(user_input)

    def detect_author_or_genre_fallback(self, user_input):
        """Original fallback method with minor improvements"""
        normalized_input = user_input.lower().strip()
        
        author_keywords = [
            '작가', '저자', '작품', '소설가', '시인', '문학가',
            'author', 'writer', 'books by', 'novels by', 'works by',
            '가 쓴', '의 작품', '의 책', '의 소설'
        ]
        
        genre_keywords = [
            '소설', '로맨스', '추리', '미스터리', '판타지', 'sf', '공상과학',
            '역사', '철학', '경제', '과학', '자기계발', '에세이', '시집',
            'romance', 'mystery', 'fantasy', 'thriller', 'horror', 
            'philosophy', 'history', 'economics', 'science'
        ]
        
        for keyword in author_keywords:
            if keyword in normalized_input:
                clean_name = user_input
                for remove_word in ['작가', '저자', '작품', '소설', '책', 'author', 'writer', 'books by']:
                    clean_name = re.sub(rf'\b{re.escape(remove_word)}\b', '', clean_name, flags=re.IGNORECASE)
                clean_name = clean_name.strip()
                if clean_name:
                    return ("AUTHOR", clean_name)
        
        korean_surnames = ['김', '박', '이', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안', '송', '류', '전']
        has_korean_surname = any(surname in user_input for surname in korean_surnames)
        words = user_input.split()
        has_western_name_pattern = len(words) >= 2 and any(word[0].isupper() and len(word) > 1 for word in words)
        
        famous_authors = [
            '하루키', '헤밍웨이', '톨스토이', '도스토옙스키', '카프카', '조이스',
            'king', 'rowling', 'christie', 'shakespeare', 'hemingway'
        ]
        has_famous_author = any(author.lower() in normalized_input for author in famous_authors)
        
        if has_korean_surname or has_western_name_pattern or has_famous_author:
            genre_indicators = ['추천', '소개', '목록', '리스트', '종류', '분야', '관련']
            is_genre_request = any(indicator in normalized_input for indicator in genre_indicators) and \
                              any(genre in normalized_input for genre in genre_keywords)
            if not is_genre_request:
                return ("AUTHOR", user_input.strip())
        
        if any(genre in normalized_input for genre in genre_keywords):
            return ("GENRE", user_input)
        
        if len(words) <= 3 and (has_korean_surname or has_western_name_pattern):
            return ("AUTHOR", user_input.strip())
        
        return ("GENRE", user_input)

    def extract_genre_keywords(self, user_input, api_key, dtl_kdc_dict, headers):
        """Original genre-based keyword extraction logic with exact match priority and debug print."""
        # First attempt - exact keyword matching
        for code, label in dtl_kdc_dict.items():
            if user_input.strip().replace(' ', '') == label.strip().replace(' ', ''):
                print(f"[DEBUG] [GENRE EXTRACTION] Exact match: '{user_input}' -> '{label}' (code: {code})")
                return code, label

        categories_list = []
        for code, label in dtl_kdc_dict.items():
            categories_list.append(f"- {code}: {label}")
        categories_text = "\n".join(categories_list)
        # First prompt - look for exact keywords
        prompt_exact = f"""
다음은 전체 도서 분류 코드 목록입니다:
{categories_text}

사용자 입력: "{user_input}"

위의 전체 목록에서 사용자 입력과 정확히 일치하는 키워드나 분류명을 찾아주세요.
예를 들어:
- "영문학" → 영미문학 관련 코드
- "역사" → 역사 관련 코드  
- "소설" → 소설 관련 코드
- "철학" → 철학 관련 코드

정확한 일치가 있으면 해당 코드번호만 반환하세요. 정확한 일치가 없으면 "NO_EXACT_MATCH"를 반환하세요.
"""
        data_exact = {
            "messages": [
                {
                    "role": "system",
                    "content": "당신은 도서 분류 전문가입니다. 전체 분류 목록에서 정확한 키워드 일치를 찾아 코드번호만 반환합니다."
                },
                {
                    "role": "user", 
                    "content": prompt_exact
                }
            ],
            "maxTokens": 50,
            "temperature": 0.1,
            "topP": 0.5,
        }
        try:
            # First API call - exact matching
            response = requests.post(
                "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
                headers=headers,
                json=data_exact,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                extracted_code = result['result']['message']['content'].strip()
                extracted_code = extracted_code.replace('"', '').replace("'", '').strip()
                print(f"[DEBUG] [GENRE EXTRACTION] HyperCLOVA extracted keyword/code: '{extracted_code}'")
                # If exact match found and exists in dictionary
                if extracted_code != "NO_EXACT_MATCH" and extracted_code in dtl_kdc_dict:
                    return extracted_code, dtl_kdc_dict[extracted_code]
                # If no exact match, try second attempt with similarity
                prompt_similar = f"""
사용자 입력: "{user_input}"

다음은 사용할 수 있는 도서 분류 코드들입니다:
{categories_text}

정확한 일치가 없으므로, 사용자 입력의 의미와 가장 유사한 분류 코드를 찾아주세요.
의미상 연관성을 고려하여 가장 적절한 코드를 선택하세요.

예를 들어:
- "책 추천" → 일반적인 문학이나 총류 관련 코드
- "경제 관련" → 경제학 관련 코드
- "건강" → 의학이나 건강 관련 코드
- "요리" → 요리, 음식 관련 코드

가장 유사한 코드번호만 반환하세요.
"""
                data_similar = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 도서 분류 전문가입니다. 의미적 유사성을 바탕으로 가장 적절한 분류 코드를 찾아 반환합니다."
                        },
                        {
                            "role": "user", 
                            "content": prompt_similar
                        }
                    ],
                    "maxTokens": 50,
                    "temperature": 0.3,
                    "topP": 0.7,
                }
                # Second API call - similarity matching
                response2 = requests.post(
                    "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
                    headers=headers,
                    json=data_similar,
                    timeout=30
                )
                if response2.status_code == 200:
                    result2 = response2.json()
                    similar_code = result2['result']['message']['content'].strip()
                    similar_code = similar_code.replace('"', '').replace("'", '').strip()
                    print(f"[DEBUG] [GENRE EXTRACTION] HyperCLOVA similarity keyword/code: '{similar_code}'")
                    if similar_code in dtl_kdc_dict:
                        return similar_code, dtl_kdc_dict[similar_code]
                    else:
                        # Try to find partial matches
                        return self.find_best_dtl_code_fallback(user_input, dtl_kdc_dict, similar_code)
                else:
                    return self.find_best_dtl_code_fallback(user_input, dtl_kdc_dict)
            else:
                return self.find_best_dtl_code_fallback(user_input, dtl_kdc_dict)
        except Exception:
            return self.find_best_dtl_code_fallback(user_input, dtl_kdc_dict)

    def find_best_dtl_code_fallback(self, user_query, dtl_kdc_dict, ai_suggested_code=None):
        """Fallback method to find the best matching DTL KDC code"""
        best_score = 0
        best_code = None
        best_label = ""
        
        # If AI suggested a code but it wasn't exact, try to find similar codes
        if ai_suggested_code:
            for code, label in dtl_kdc_dict.items():
                if ai_suggested_code in code or code in ai_suggested_code:
                    return code, label
        
        # Original similarity matching
        for code, label in dtl_kdc_dict.items():
            # Check similarity with the label
            score = SequenceMatcher(None, user_query.lower(), label.lower()).ratio()
            
            # Also check if any word from user query is in the label
            user_words = user_query.lower().split()
            for word in user_words:
                if len(word) > 1 and word in label.lower():
                    score += 0.3  # Boost score for word matches
            
            if score > best_score:
                best_score = score
                best_code = code
                best_label = label
        
        return best_code, best_label if best_score > 0.2 else (None, None)

    def get_dtl_kdc_code(self, user_query, api_key=None):
        """Enhanced DTL KDC code detection with better author/genre classification and exact label match."""
        api_key = api_key or self.hyperclova_api_key

        # 1. Exact label match (case-insensitive, strip spaces)
        for code, label in self.dtl_kdc_dict.items():
            if user_query.strip().replace(' ', '') == label.strip().replace(' ', ''):
                return code, label

        if api_key:
            try:
                # Use HyperCLOVA for classification
                result = self.extract_keywords_with_hyperclova(user_query, api_key)
                
                # Handle author requests
                if isinstance(result, tuple) and len(result) == 2 and result[0] == "AUTHOR":
                    author_name = result[1]
                    return "AUTHOR", author_name
                
                # Handle genre requests
                elif isinstance(result, tuple) and len(result) == 2 and result[0] == "GENRE":
                    user_input = result[1]
                    
                    # Use the existing genre extraction logic
                    code, label = self.extract_genre_keywords(user_input, api_key, self.dtl_kdc_dict, {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    })
                    
                    if code and label:
                        return code, label
                    else:
                        return None, None
                
                # Fallback if HyperCLOVA result is unexpected
                else:
                    return self.handle_fallback_classification(user_query)
                    
            except Exception:
                return self.handle_fallback_classification(user_query)
        
        # No API key available
        else:
            return self.handle_fallback_classification(user_query)

    def handle_fallback_classification(self, user_query):
        """Handle classification when HyperCLOVA is not available or fails"""
        fallback_result = self.detect_author_or_genre_fallback(user_query)
        
        if fallback_result[0] == "AUTHOR":
            author_name = fallback_result[1]
            return "AUTHOR", author_name
        else:
            # Try genre matching with dtl_kdc_dict
            code, label = self.find_best_dtl_code_fallback(user_query, self.dtl_kdc_dict)
            if code and label:
                return code, label
            else:
                return None, None

    def get_books_by_author(self, author_name, page_no=1, page_size=15):
        """Get books by specific author using Library API. Optionally accepts an explicit auth_key."""
        url = "http://data4library.kr/api/srchBooks"
        params = {
            "authKey": self.library_api_key,
            "author": author_name,
            "pageNo": page_no,
            "pageSize": page_size,
            "format": "json"
        }
        try:
            r = requests.get(url, params=params)
            if r.status_code == 200:
                response_data = r.json()
                if "response" in response_data and "docs" in response_data["response"]:
                    docs = response_data["response"]["docs"]
                    if isinstance(docs, dict):
                        docs = [docs]
                    elif not isinstance(docs, list):
                        return []
                    books = []
                    for doc in docs:
                        if "doc" in doc:
                            book_data = doc["doc"]
                        else:
                            book_data = doc
                        book_info = {
                            "bookname": book_data.get("bookname", book_data.get("bookName", "제목 없음")),
                            "authors": book_data.get("authors", book_data.get("author", "저자 미상")),
                            "publisher": book_data.get("publisher", "출판사 미상"),
                            "publication_year": book_data.get("publication_year", book_data.get("publicationYear", "출간년도 미상")),
                            "isbn13": book_data.get("isbn13", book_data.get("isbn", "")),
                            "loan_count": int(book_data.get("loan_count", book_data.get("loanCount", 0))),
                            "bookImageURL": book_data.get("bookImageURL", ""),
                            "bookDtlUrl": book_data.get("bookDtlUrl", "")
                        }
                        books.append(book_info)
                    books = sorted(books, key=lambda x: (x.get("publication_year", "0"), x["loan_count"]), reverse=True)
                    return books
                else:
                    return []
        except Exception:
            return []
        return []

    def get_books_by_dtl_kdc(self, dtl_kdc_code, page_no=1, page_size=15):
        """Get books using DTL KDC code"""
        if not self.library_api_key:
            return []
            
        url = "http://data4library.kr/api/loanItemSrch"
        params = {
            "authKey": self.library_api_key,
            "startDt": "2000-01-01",
            "endDt": datetime.now().strftime("%Y-%m-%d"),
            "format": "json",
            "pageNo": page_no,
            "pageSize": page_size,
            "dtl_kdc": dtl_kdc_code  # Use dtl_kdc parameter
        }
        
        try:
            r = requests.get(url, params=params)
            if r.status_code == 200:
                response_data = r.json()
                
                # Check if response has the expected structure
                if "response" in response_data:
                    docs = response_data["response"].get("docs", [])
                    
                    # Handle case where docs might be a single dict instead of list
                    if isinstance(docs, dict):
                        docs = [docs]
                    elif not isinstance(docs, list):
                        return []
                    
                    # Extract and clean book data
                    books = []
                    for doc in docs:
                        # Handle nested 'doc' structure if it exists
                        if "doc" in doc:
                            book_data = doc["doc"]
                        else:
                            book_data = doc
                        
                        # Extract book information with fallback values
                        book_info = {
                            "bookname": book_data.get("bookname", book_data.get("bookName", "제목 없음")),
                            "authors": book_data.get("authors", book_data.get("author", "저자 미상")),
                            "publisher": book_data.get("publisher", "출판사 미상"),
                            "publication_year": book_data.get("publication_year", book_data.get("publicationYear", "출간년도 미상")),
                            "isbn13": book_data.get("isbn13", book_data.get("isbn", "")),
                            "loan_count": int(book_data.get("loan_count", book_data.get("loanCount", 0))),
                            "bookImageURL": book_data.get("bookImageURL", "")
                        }
                        books.append(book_info)
                    
                    # Sort by loan count (descending)
                    books = sorted(books, key=lambda x: x["loan_count"], reverse=True)
                    return books
                else:
                    return []
        except Exception:
            return []
        
        return []

    def get_popular_books_by_location(self, location_code, page_no=1, page_size=15, dtl_kdc_code=None):
        """Get popular books by location with optional genre filtering using Library API"""
        if not self.library_api_key:
            return []
            
        if location_code:
            url = "http://data4library.kr/api/loanItemSrchByLib"
            params = {
                "authKey": self.library_api_key,
                "dtl_region": location_code,
                "pageNo": page_no,
                "pageSize": page_size,
                "format": "json"
            }
            
            # Add genre filter if provided
            if dtl_kdc_code:
                params["dtl_kdc"] = dtl_kdc_code
                
        else:
            # If no location, get overall popular books
            url = "http://data4library.kr/api/loanItemSrch"
            params = {
                "authKey": self.library_api_key,
                "startDt": "2023-01-01",
                "endDt": datetime.now().strftime("%Y-%m-%d"),
                "pageNo": page_no,
                "pageSize": page_size,
                "format": "json"
            }
            
            # Add genre filter if provided
            if dtl_kdc_code:
                params["dtl_kdc"] = dtl_kdc_code
        
        try:
            r = requests.get(url, params=params)
            if r.status_code == 200:
                response_data = r.json()
                
                if "response" in response_data:
                    docs = response_data["response"].get("docs", [])
                    
                    if isinstance(docs, dict):
                        docs = [docs]
                    elif not isinstance(docs, list):
                        return []
                    
                    books = []
                    for doc in docs:
                        if "doc" in doc:
                            book_data = doc["doc"]
                        else:
                            book_data = doc
                        
                        book_info = {
                            "bookname": book_data.get("bookname", "제목 없음"),
                            "authors": book_data.get("authors", "저자 미상"),
                            "publisher": book_data.get("publisher", "출판사 미상"),
                            "publication_year": book_data.get("publication_year", "출간년도 미상"),
                            "isbn13": book_data.get("isbn13", ""),
                            "loan_count": int(book_data.get("loan_count", 0)),
                            "bookImageURL": book_data.get("bookImageURL", "")
                        }
                        books.append(book_info)
                    
                    return sorted(books, key=lambda x: x["loan_count"], reverse=True)
                else:
                    return []
        except Exception:
            return []
        
        return []

    def process_followup_with_hyperclova(self, user_input, api_key=None, conversation_context=""):
        """Process follow-up questions using HyperCLOVA API"""
        api_key = api_key or self.hyperclova_api_key
        if not api_key:
            return "자세한 답변을 받으려면 HyperCLOVA API 키를 제공해 주세요."
        
        prompt = f"""
이전 대화 내용:
{conversation_context}

사용자의 새로운 질문: "{user_input}"

위의 맥락을 고려하여 사용자의 질문에 대해 도움이 되는 답변을 해주세요. 
만약 새로운 도서 추천을 요청하는 것 같다면, 구체적인 장르나 주제를 제시해주세요.

답변은 한국어로만 제공해주세요.
"""
        
        messages = [
            {
                "role": "system",
                "content": "당신은 도서 추천 전문가입니다. 사용자와의 대화 맥락을 이해하고 도움이 되는 답변을 제공합니다. 항상 한국어로만 답변하세요."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        return self.call_hyperclova_api(messages, api_key)

    def generate_book_introduction(self, book, api_key=None):
        """Generate an introduction about the book when first selected"""
        api_key = api_key or self.hyperclova_api_key
        title = book.get('bookname') or book.get('bookName', '제목 없음')
        authors = book.get('authors') or book.get('author', '저자 미상')
        publisher = book.get('publisher', '출판사 미상')
        year = book.get('publication_year') or book.get('publicationYear', '출간년도 미상')
        loan_count = book.get('loan_count') or book.get('loanCount', 0)
        
        if not api_key:
            return f"{authors}의 '{title}'에 대해 이야기해 봅시다! 이 책은 {year}년에 {publisher}에서 출간되었으며 {loan_count}번 대출되어 인기를 보여줍니다. 이 책에 대해 무엇을 알고 싶으신가요 - 주제, 줄거리, 문체, 아니면 비슷한 추천을 원하시나요?"
        
        book_context = f"도서: {title}, 저자: {authors}, 출판사: {publisher}, 출간년도: {year}, 대출횟수: {loan_count}회"
        
        messages = [
            {
                "role": "system",
                "content": "당신은 지식이 풍부한 도서 전문가입니다. 모든 답변은 한국어로만 제공하세요. 도서에 대한 매력적인 소개를 제공하세요."
            },
            {
                "role": "user", 
                "content": f"다음 도서에 대한 매력적인 소개를 제공해주세요: {book_context}. 이 책이 흥미로운 이유, 잠재적 주제에 대해 이야기하고 사용자가 질문을 할 수 있도록 유도해주세요. 대화식으로 친근하게 작성해주세요."
            }
        ]
        
        response = self.call_hyperclova_api(messages, api_key)
        if response:
            return response
        else:
            # Fallback if API fails
            return f"{authors}의 '{title}'을 탐험해 봅시다! {publisher}({year})의 이 책은 {loan_count}번의 대출로 독자들에게 어필하고 있음을 보여줍니다. 줄거리 세부사항부터 주제 분석까지 이 책에 대한 모든 것을 논의할 준비가 되어 있습니다. 어떤 측면에 가장 관심이 있으신가요?"

    def process_book_question(self, book, question, api_key=None, conversation_history=""):
        """Process specific questions about a book using HyperCLOVA with improved context handling"""
        api_key = api_key or self.hyperclova_api_key
        if not api_key:
            return "이 책에 대한 자세한 답변을 받으려면 HyperCLOVA API 키를 제공해 주세요."
        
        title = book.get('bookname') or book.get('bookName', '제목 없음')
        authors = book.get('authors') or book.get('author', '저자 미상')
        publisher = book.get('publisher', '출판사 미상')
        year = book.get('publication_year') or book.get('publicationYear', '출간년도 미상')
        loan_count = book.get('loan_count') or book.get('loanCount', 0)
        
        book_info = f"제목: '{title}', 저자: {authors}, 출판사: {publisher}, 출간년도: {year}, 인기도: {loan_count}회 대출"
        
        # Enhanced prompt with better context integration
        enhanced_prompt = f"""
현재 논의 중인 도서 정보:
{book_info}

이전 대화 내용:
{conversation_history}

사용자의 새로운 질문: "{question}"

위의 도서와 이전 대화 맥락을 모두 고려하여 사용자의 질문에 대해 상세하고 도움이 되는 답변을 제공해주세요.

답변 지침:
1. 이전 대화의 맥락을 참고하여 연속성 있는 답변을 제공하세요
2. 책의 내용, 주제, 등장인물, 문체, 문화적 배경 등에 대해 구체적으로 설명하세요
3. 필요시 유사한 책 추천도 포함하세요
4. 답변은 한국어로만 제공하세요
5. 답변은 상세하고 통찰력 있게 작성해주세요.
"""
        
        messages = [
            {
                "role": "system",
                "content": f"당신은 '{title}' by {authors}에 대해 논의하는 지식이 풍부한 도서 전문가입니다. 이전 대화의 맥락을 기억하고 연속성 있는 답변을 제공합니다. 모든 답변은 한국어로만 제공하며, 도서의 주제, 줄거리 요소, 등장인물 분석, 문체, 문화적 맥락, 유사한 도서 추천 등을 포함한 상세하고 통찰력 있는 정보를 제공합니다."
            },
            {
                "role": "user",
                "content": enhanced_prompt
            }
        ]
        
        try:
            response = self.call_hyperclova_api(messages, api_key)
            if response:
                return response
            else:
                return f"'{title}'에 대한 논의를 계속하고 싶지만 지금 AI 서비스에 연결하는 데 문제가 있습니다. 질문을 다시 해보시겠어요?"
        except Exception:
            return f"'{title}'에 대한 질문을 처리하는 중 오류가 발생했습니다. 질문을 다시 표현하거나 API 연결을 확인해 주세요."

    def extract_location_code_with_hyperclova(self, user_input, api_key=None):
        """Extract the best matching location code (city or district) from user input using HyperCLOVA and dtl_region.json."""
        api_key = api_key or self.hyperclova_api_key
        if not api_key or not self.location_data:
            return None, None, None
        # Build a location list string for the prompt
        location_list = '\n'.join([
            f"{item['code']}: {item['city']} {item['district']}" for item in self.location_data
        ])
        prompt = f"""
아래는 대한민국의 시/도 및 구/군 목록과 코드입니다. 사용자 입력에서 가장 관련 있는 지역(도시 또는 구/군)을 찾아 해당 코드를 반환하세요.

지역 목록:
{location_list}

사용자 입력: "{user_input}"

응답 형식: "CODE:코드, CITY:도시명, DISTRICT:구/군명"
예시: CODE:11010, CITY:서울특별시, DISTRICT:종로구

만약 적절한 지역이 없으면 "NONE"이라고 답하세요.
"""
        data = {
            "messages": [
                {"role": "system", "content": "당신은 지역명 추출 전문가입니다. 반드시 위 응답 형식만 사용하세요."},
                {"role": "user", "content": prompt}
            ],
            "maxTokens": 50,
            "temperature": 0.1,
            "topP": 0.3,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(
                "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
                headers=headers,
                json=data,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                content = result['result']['message']['content'].strip()
                if content.startswith("CODE:"):
                    parts = content.split(',')
                    code = parts[0].split(':')[1].strip()
                    city = parts[1].split(':')[1].strip() if len(parts) > 1 else ''
                    district = parts[2].split(':')[1].strip() if len(parts) > 2 else ''
                    return code, city, district
                elif content.strip().upper() == "NONE":
                    return None, None, None
            return None, None, None
        except Exception:
            return None, None, None

# Helper functions
def normalize_text(text):
    if not isinstance(text, str):
        return ''
    text = unicodedata.normalize('NFKC', text)
    text = text.strip().lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ''.join(text.split())
    return text

def find_kdc_code_exact(dtl_kdc_dict, keyword):
    keyword_clean = normalize_text(keyword)
    print(f"[DEBUG] [EXACT] User input: {repr(keyword)} | Normalized: {repr(keyword_clean)}")
    print("[DEBUG] All loaded labels from dtl_kdc_dict:")
    for code, label in dtl_kdc_dict.items():
        print(f"  code={code}, label={repr(label)}")
    for code, label in dtl_kdc_dict.items():
        label_clean = normalize_text(label)
        print(f"[DEBUG] [EXACT] Comparing with label: {repr(label)} | Normalized: {repr(label_clean)}")
        if keyword_clean == label_clean:
            print(f"[DEBUG] [EXACT] Match found: code={code}, label={label}")
            return code, label
    print("[DEBUG] [EXACT] No exact match found. All labels:")
    for code, label in dtl_kdc_dict.items():
        print(f"  code={code}, label={repr(label)} -> normalized={repr(normalize_text(label))}")
    return None, None

def find_kdc_code_approximate(dtl_kdc_dict, keyword):
    keyword_clean = normalize_text(keyword)
    best_score = 0
    best_code = None
    best_label = None
    for code, label in dtl_kdc_dict.items():
        label_clean = normalize_text(label)
        score = SequenceMatcher(None, keyword_clean, label_clean).ratio()
        print(f"[DEBUG] [SIM] Comparing: {repr(keyword_clean)} vs {repr(label_clean)} | Score: {score}")
        if score > best_score:
            best_score = score
            best_code = code
            best_label = label
    if best_score > 0.4:
        print(f"[DEBUG] [SIM] Best match: code={best_code}, label={best_label}, score={best_score}")
        return best_code, best_label
    print("[DEBUG] [SIM] No approximate match found.")
    return None, None

def extract_keyword_with_hyperclova_for_label(user_input, api_key):
    prompt = f"""
다음 사용자 입력에서 도서 분류에 해당하는 가장 핵심적인 한 단어(예: 철학, 역사, 소설, 경제, 음악, 수학, 문학, 언어, 예술, 정치, 종교, 과학, 기술, 의학, 건축, 심리학, 교육학 등)만 뽑아서 반환하세요. 반드시 한 단어만 반환하세요. 만약 적절한 키워드가 없으면 '일반'이라고 답하세요.\n\n사용자 입력: {user_input}\n\n키워드:"""
    data = {
        "messages": [
            {"role": "system", "content": "당신은 도서 분류 키워드 추출 전문가입니다. 반드시 한 단어만 반환하세요."},
            {"role": "user", "content": prompt}
        ],
        "maxTokens": 10,
        "temperature": 0.1,
        "topP": 0.5,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(
            "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=data,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            keyword = result['result']['message']['content'].strip().replace('"', '').replace("'", '').strip()
            if keyword and keyword != '일반':
                return keyword
    except Exception as e:
        print(f"[DEBUG] 키워드 추출 실패: {e}")
    return None

def get_dtl_kdc_code(user_query, api_key, dtl_kdc_dict):
    """DTL KDC code detection: HyperCLOVA extracts a single keyword, then match to JSON labels."""
    keyword = extract_keyword_with_hyperclova_for_label(user_query, api_key)
    if not keyword:
        return None, None
    code, label = find_kdc_code_exact(dtl_kdc_dict, keyword)
    if code:
        return code, label
    # Only try similarity if exact match failed
    code, label = find_kdc_code_approximate(dtl_kdc_dict, keyword)
    if code:
        return code, label
    # Fallback: try to match the whole user query
    code, label = find_kdc_code_exact(dtl_kdc_dict, user_query)
    if not code:
        code, label = find_kdc_code_approximate(dtl_kdc_dict, user_query)
    return code, label

def is_probable_person_name(name, user_query):
    """Return True if name looks like a real person (Korean or Western), False otherwise."""
    # Not the whole query, not too long
    if not name or name.strip() == '' or name.strip() == user_query.strip():
        return False
    if len(name) > 30:
        return False
    # Should be 2-4 words (Korean or English)
    words = name.strip().split()
    if len(words) > 4 or len(words) < 1:
        return False
    # Should not contain location or domain keywords
    location_keywords = [
        '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주',
        '특별시', '광역시', '도', '시', '구', '군', '지역', '도서관'
    ]
    domain_keywords = [
        '책', '도서', '소설', '문학', '장르', '분야', '추천', '인기', '관련', '영어', '역사', '철학', '과학', '경제', '자기계발', '에세이', '시집',
        'romance', 'mystery', 'fantasy', 'thriller', 'horror', 'philosophy', 'history', 'economics', 'science'
    ]
    for kw in location_keywords + domain_keywords:
        if kw in name:
            return False
    # Simple regex for Korean or English names
    if re.match(r'^[가-힣]{2,4}$', name.replace(' ', '')):
        return True
    if re.match(r'^[A-Za-z\-\.\s]{2,30}$', name):
        return True
    return False

def process_user_message(user_message):
    """
    Robustly handle user input for author, domain, and location+domain queries.
    """
    import json as pyjson
    service = LibraryAPIService(
        hyperclova_api_key=getattr(settings, 'HYPERCLOVA_API_KEY', None),
        library_api_key=getattr(settings, 'LIBRARY_API_KEY', None)
    )
    api_key = getattr(settings, 'HYPERCLOVA_API_KEY', None)
    dtl_kdc_dict = service.dtl_kdc_dict
    print(f"[DEBUG] [USER INPUT] {repr(user_message)}")
    # Try to extract location first
    location_code, city, district = service.extract_location_code_with_hyperclova(user_message, api_key)
    print(f"[DEBUG] [LOCATION EXTRACTION] code={location_code}, city={city}, district={district}")
    # Try to extract author/domain
    classification_result = service.get_dtl_kdc_code(user_message, api_key)
    print(f"[DEBUG] [CLASSIFICATION RESULT] {classification_result}")
    # 1. Location + Domain (robust)
    if location_code:
        # If classifier says AUTHOR, check if it's a real person
        if classification_result and classification_result[0] == "AUTHOR":
            author_name = classification_result[1]
            if is_probable_person_name(author_name, user_message):
                books = service.get_books_by_author(author_name, page_size=15)
                print(f"[DEBUG] Library API가 작가 '{author_name}'에 대해 {len(books)}권의 책을 반환했습니다")
                if books:
                    book_lines = []
                    book_jsons = []
                    for i, b in enumerate(books[:15]):
                        book_lines.append(f"{i+1}. 제목: {b['bookname']}\n   저자: {b['authors']}\n   출판사: {b['publisher']}\n   출판연도: {b['publication_year']}\n   대출 횟수: {b['loan_count']}")
                        book_jsons.append(pyjson.dumps({
                            'title': b['bookname'],
                            'author': b['authors'],
                            'publisher': b['publisher'],
                            'year': b['publication_year'],
                            'loan': b['loan_count'],
                            'cover': b.get('bookImageURL', '')
                        }, ensure_ascii=False))
                    book_list = '\n\n'.join(book_lines)
                    book_json_block = '\n'.join(book_jsons)
                    return f"'{author_name}' 작가의 인기 도서 목록입니다:\n\n{book_list}\n\nBOOKLIST_JSON:\n{book_json_block}"
                else:
                    return f"'{author_name}' 작가의 도서를 찾을 수 없습니다. 다른 작가명을 입력해 주세요."
            # Not a real person, fallback to domain extraction
            else:
                # Try to extract domain (KDC code) again
                code, label = None, None
                if isinstance(classification_result, tuple) and len(classification_result) == 2 and classification_result[0] in dtl_kdc_dict:
                    code, label = classification_result
                else:
                    code, label = get_dtl_kdc_code(user_message, api_key, dtl_kdc_dict)
                if code:
                    books = service.get_popular_books_by_location(location_code, page_size=15, dtl_kdc_code=code)
                    print(f"[DEBUG] [LOCATION+DOMAIN-FALLBACK] {city} {district} / {label} => {len(books)} books")
                    if books:
                        book_lines = []
                        book_jsons = []
                        for i, b in enumerate(books[:15]):
                            book_lines.append(f"{i+1}. 제목: {b['bookname']}\n   저자: {b['authors']}\n   출판사: {b['publisher']}\n   출판연도: {b['publication_year']}\n   대출 횟수: {b['loan_count']}")
                            book_jsons.append(pyjson.dumps({
                                'title': b['bookname'],
                                'author': b['authors'],
                                'publisher': b['publisher'],
                                'year': b['publication_year'],
                                'loan': b['loan_count'],
                                'cover': b.get('bookImageURL', '')
                            }, ensure_ascii=False))
                        book_list = '\n\n'.join(book_lines)
                        book_json_block = '\n'.join(book_jsons)
                        return f"'{city} {district}' 지역의 '{label}' 분야 인기 도서 목록입니다:\n\n{book_list}\n\nBOOKLIST_JSON:\n{book_json_block}"
                    else:
                        return f"'{city} {district}' 지역의 '{label}' 분야 도서를 찾을 수 없습니다. 다른 키워드를 입력해 주세요."
                else:
                    return f"'{city} {district}' 지역의 도서 분류를 찾을 수 없습니다. 다른 키워드를 입력해 주세요."
        # If classifier says GENRE/DOMAIN
        elif classification_result and (isinstance(classification_result, tuple) and len(classification_result) == 2 and classification_result[0] in dtl_kdc_dict):
            code, label = classification_result
            books = service.get_popular_books_by_location(location_code, page_size=15, dtl_kdc_code=code)
            print(f"[DEBUG] [LOCATION+DOMAIN] {city} {district} / {label} => {len(books)} books")
            if books:
                book_lines = []
                book_jsons = []
                for i, b in enumerate(books[:15]):
                    book_lines.append(f"{i+1}. 제목: {b['bookname']}\n   저자: {b['authors']}\n   출판사: {b['publisher']}\n   출판연도: {b['publication_year']}\n   대출 횟수: {b['loan_count']}")
                    book_jsons.append(pyjson.dumps({
                        'title': b['bookname'],
                        'author': b['authors'],
                        'publisher': b['publisher'],
                        'year': b['publication_year'],
                        'loan': b['loan_count'],
                        'cover': b.get('bookImageURL', '')
                    }, ensure_ascii=False))
                book_list = '\n\n'.join(book_lines)
                book_json_block = '\n'.join(book_jsons)
                return f"'{city} {district}' 지역의 '{label}' 분야 인기 도서 목록입니다:\n\n{book_list}\n\nBOOKLIST_JSON:\n{book_json_block}"
            else:
                return f"'{city} {district}' 지역의 '{label}' 분야 도서를 찾을 수 없습니다. 다른 키워드를 입력해 주세요."
        # If location only, fallback to popular books by location
        else:
            books = service.get_popular_books_by_location(location_code, page_size=15)
            print(f"[DEBUG] [LOCATION ONLY] {city} {district} => {len(books)} books")
            if books:
                book_lines = []
                book_jsons = []
                for i, b in enumerate(books[:15]):
                    book_lines.append(f"{i+1}. 제목: {b['bookname']}\n   저자: {b['authors']}\n   출판사: {b['publisher']}\n   출판연도: {b['publication_year']}\n   대출 횟수: {b['loan_count']}")
                    book_jsons.append(pyjson.dumps({
                        'title': b['bookname'],
                        'author': b['authors'],
                        'publisher': b['publisher'],
                        'year': b['publication_year'],
                        'loan': b['loan_count'],
                        'cover': b.get('bookImageURL', '')
                    }, ensure_ascii=False))
                book_list = '\n\n'.join(book_lines)
                book_json_block = '\n'.join(book_jsons)
                return f"'{city} {district}' 지역의 인기 도서 목록입니다:\n\n{book_list}\n\nBOOKLIST_JSON:\n{book_json_block}"
            else:
                return f"'{city} {district}' 지역의 도서를 찾을 수 없습니다. 다른 키워드를 입력해 주세요."
    # 2. Author only (no location)
    elif classification_result and classification_result[0] == "AUTHOR":
        author_name = classification_result[1]
        if is_probable_person_name(author_name, user_message):
            books = service.get_books_by_author(author_name, page_size=15)
            print(f"[DEBUG] Library API가 작가 '{author_name}'에 대해 {len(books)}권의 책을 반환했습니다")
            if books:
                book_lines = []
                book_jsons = []
                for i, b in enumerate(books[:15]):
                    book_lines.append(f"{i+1}. 제목: {b['bookname']}\n   저자: {b['authors']}\n   출판사: {b['publisher']}\n   출판연도: {b['publication_year']}\n   대출 횟수: {b['loan_count']}")
                    book_jsons.append(pyjson.dumps({
                        'title': b['bookname'],
                        'author': b['authors'],
                        'publisher': b['publisher'],
                        'year': b['publication_year'],
                        'loan': b['loan_count'],
                        'cover': b.get('bookImageURL', '')
                    }, ensure_ascii=False))
                book_list = '\n\n'.join(book_lines)
                book_json_block = '\n'.join(book_jsons)
                return f"'{author_name}' 작가의 인기 도서 목록입니다:\n\n{book_list}\n\nBOOKLIST_JSON:\n{book_json_block}"
            else:
                return f"'{author_name}' 작가의 도서를 찾을 수 없습니다. 다른 작가명을 입력해 주세요."
        else:
            # Fallback to domain only
            code, label = get_dtl_kdc_code(user_message, api_key, dtl_kdc_dict)
            if code:
                books = service.get_books_by_dtl_kdc(code, page_size=15)
                print(f"[DEBUG] Library API가 코드={code}, 라벨={label}에 대해 {len(books)}권의 책을 반환했습니다")
                if books:
                    book_lines = []
                    book_jsons = []
                    for i, b in enumerate(books[:15]):
                        book_lines.append(f"{i+1}. 제목: {b['bookname']}\n   저자: {b['authors']}\n   출판사: {b['publisher']}\n   출판연도: {b['publication_year']}\n   대출 횟수: {b['loan_count']}")
                        book_jsons.append(pyjson.dumps({
                            'title': b['bookname'],
                            'author': b['authors'],
                            'publisher': b['publisher'],
                            'year': b['publication_year'],
                            'loan': b['loan_count'],
                            'cover': b.get('bookImageURL', '')
                        }, ensure_ascii=False))
                    book_list = '\n\n'.join(book_lines)
                    book_json_block = '\n'.join(book_jsons)
                    return f"'{label}' 분야의 인기 도서 목록입니다:\n\n{book_list}\n\nBOOKLIST_JSON:\n{book_json_block}"
                else:
                    return f"'{label}' 분야의 도서를 찾을 수 없습니다. 다른 키워드를 입력해 주세요."
            else:
                return "입력하신 내용과 일치하는 도서 분류를 찾을 수 없습니다. 다른 키워드를 입력해 주세요."
    # 3. Domain only (no location, no author)
    elif classification_result and (isinstance(classification_result, tuple) and len(classification_result) == 2 and classification_result[0] in dtl_kdc_dict):
        code, label = classification_result
        books = service.get_books_by_dtl_kdc(code, page_size=15)
        print(f"[DEBUG] Library API가 코드={code}, 라벨={label}에 대해 {len(books)}권의 책을 반환했습니다")
        if books:
            book_lines = []
            book_jsons = []
            for i, b in enumerate(books[:15]):
                book_lines.append(f"{i+1}. 제목: {b['bookname']}\n   저자: {b['authors']}\n   출판사: {b['publisher']}\n   출판연도: {b['publication_year']}\n   대출 횟수: {b['loan_count']}")
                book_jsons.append(pyjson.dumps({
                    'title': b['bookname'],
                    'author': b['authors'],
                    'publisher': b['publisher'],
                    'year': b['publication_year'],
                    'loan': b['loan_count'],
                    'cover': b.get('bookImageURL', '')
                }, ensure_ascii=False))
            book_list = '\n\n'.join(book_lines)
            book_json_block = '\n'.join(book_jsons)
            return f"'{label}' 분야의 인기 도서 목록입니다:\n\n{book_list}\n\nBOOKLIST_JSON:\n{book_json_block}"
        else:
            print("[DEBUG] [FAIL] No books found for code.")
            return f"'{label}' 분야의 도서를 찾을 수 없습니다. 다른 키워드를 입력해 주세요."
    else:
        print("[DEBUG] [FAIL] No valid classification or location found.")
        return "입력하신 내용과 일치하는 도서 분류 또는 지역/작가를 찾을 수 없습니다. 다른 키워드를 입력해 주세요."
