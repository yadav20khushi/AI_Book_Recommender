# import requests
# import os

# from django.utils import timezone

# from apps.recommendations.models import ChatHistory, UserHistory
# from apps.books.models import Book
# from django.contrib.auth.models import User


# class ClovaBookChatHandler:
#     CLOVA_API_URL = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"
#     CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")

#     def __init__(self, username: str):
#         self.username = username

#     def generate_prompt(self, title: str, author: str, description: str) -> str:
#         return (
#             f"책을 소개해 주세요. 저는 이 책에 대해 궁금한 독자입니다.\n"
#             f"제목: {title}\n저자: {author}\n설명: {description}\n\n"
#             f"이 책의 주요 내용과 특징을 쉽게 설명해 주세요."
#         )

#     def call_clova(self, messages: list[dict]) -> str:
#         headers = {
#             "Authorization": f"Bearer {self.CLOVA_API_KEY}",
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "messages": messages,
#             "maxTokens": 1024,
#             "temperature": 0.7,
#             "topP": 0.8,
#         }

#         try:
#             response = requests.post(self.CLOVA_API_URL, headers=headers, json=payload)
#             response.raise_for_status()
#             result = response.json()

#             print("Clova Raw Response:", result)

#             msg = result.get("result", {}).get("message", {})
#             if "content" in msg:
#                 return msg["content"]
#             else:
#                 return f"Clova 응답이 예상과 다릅니다: {result}"

#         except Exception as e:
#             print("Clova API call failed:", e)
#             try:
#                 print("Error response body:", response.text)
#             except:
#                 pass
#             return f"Clova API 호출에 실패했습니다: {e}"

#     def save_user_history(self, book_data: dict, clova_response: str):

#         title = book_data.get("title", "제목 없음")
#         author = book_data.get("authors", "저자 정보 없음")
#         description = book_data.get("description", "설명 없음")
#         isbn13 = book_data.get("isbn13", "N/A")
#         cover = book_data.get("cover", "")

#         # Ensure book exists
#         book_obj, _ = Book.objects.get_or_create(
#             isbn13=isbn13,
#             defaults={
#                 "title": title,
#                 "author": author,
#                 "summary": description,
#                 "cover_url": cover
#             }
#         )

#         # Fetch actual Django User object
#         user = User.objects.filter(username=self.username).first()

#         if not user:
#             return  # Or raise error

#         # Create a new UserHistory entry (now linked to Django user FK)
#         user_history = UserHistory.objects.create(
#             user=user,
#             book=book_obj,
#             session_start=timezone.now(),
#             session_end=timezone.now()
#         )

#         # Save chat history linked to the above user history
#         ChatHistory.objects.create(
#             user_history=user_history,
#             messages=[
#                 {"role": "system", "content": "당신은 책을 잘 아는 친절한 도우미입니다."},
#                 {"role": "user", "content": self.generate_prompt(title, author, description)},
#                 {"role": "assistant", "content": clova_response}
#             ]
#         )

#     def start_chat(self, book_metadata: list[dict]) -> dict:
#         if not book_metadata:
#             return {"error": "책 정보가 제공되지 않았습니다."}

#         selected = book_metadata[0]
#         title = selected.get("title", "")
#         author = selected.get("authors", "")
#         description = selected.get("description", "")

#         system_msg = {"role": "system", "content": "당신은 책을 잘 아는 친절한 도우미입니다."}
#         user_msg = {"role": "user", "content": self.generate_prompt(title, author, description)}
#         messages = [system_msg, user_msg]

#         clova_response = self.call_clova(messages)
#         self.save_user_history(selected, clova_response)

#         return {
#             "response": clova_response,
#             "session": messages + [{"role": "assistant", "content": clova_response}]
#         }

#     def followup_chat(self, session_messages: list[dict], user_input: str) -> dict:
#         session_messages.append({"role": "user", "content": user_input})
#         clova_response = self.call_clova(session_messages)
#         session_messages.append({"role": "assistant", "content": clova_response})

#         return {
#             "response": clova_response,
#             "session": session_messages
#         }



import requests
import os

from django.utils import timezone
from apps.recommendations.models import ChatHistory, UserHistory
from apps.books.models import Book
from django.contrib.auth.models import User


class ClovaBookChatHandler:
    CLOVA_API_URL = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"
    CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")

    def __init__(self, username: str):
        self.username = username
        print("📌 ClovaBookChatHandler initialized for user:", username)

    def generate_prompt(self, title: str, author: str, description: str) -> str:
        return (
            f"책을 소개해 주세요. 저는 이 책에 대해 궁금한 독자입니다.\n"
            f"제목: {title}\n저자: {author}\n설명: {description}\n\n"
            f"이 책의 주요 내용과 특징을 쉽게 설명해 주세요."
        )

    def call_clova(self, messages: list[dict]) -> str:
        headers = {
            "Authorization": f"Bearer {self.CLOVA_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "messages": messages,
            "maxTokens": 1024,
            "temperature": 0.7,
            "topP": 0.8,
        }

        try:
            response = requests.post(self.CLOVA_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()

            print("✅ Clova Raw Response:", result)

            msg = result.get("result", {}).get("message", {})
            return msg.get("content", f"⚠️ Clova 응답이 예상과 다릅니다: {result}")

        except Exception as e:
            print("❌ Clova API call failed:", e)
            try:
                print("🔴 Error response body:", response.text)
            except:
                pass
            return f"Clova API 호출에 실패했습니다: {e}"

    def save_user_history(self, book_data: dict, clova_response: str):
        print("📥 Saving user history...")

        title = book_data.get("title", "제목 없음")
        author = book_data.get("authors", "저자 정보 없음")
        description = book_data.get("description", "설명 없음")
        isbn13 = book_data.get("isbn13", "N/A")
        cover = book_data.get("cover", "")

        book_obj, created = Book.objects.get_or_create(
            isbn13=isbn13,
            defaults={
                "title": title,
                "author": author,
                "summary": description,
                "cover_url": cover
            }
        )

        if created:
            print(f"✅ Book created: {title}")
        else:
            print(f"ℹ️ Book existed: {title}")

        user = User.objects.filter(username=self.username).first()
        if not user:
            print(f"❌ No user found with username: {self.username}")
            return

        print(f"✅ Saving UserHistory for user: {user.username}, book: {title}")
        user_history = UserHistory.objects.create(
            user=user,
            book=book_obj,
            session_start=timezone.now(),
            session_end=timezone.now()
        )

        ChatHistory.objects.create(
            user_history=user_history,
            messages=[
                {"role": "system", "content": "당신은 책을 잘 아는 친절한 도우미입니다."},
                {"role": "user", "content": self.generate_prompt(title, author, description)},
                {"role": "assistant", "content": clova_response}
            ]
        )
        print("✅ ChatHistory created successfully")

    def start_chat(self, book_metadata: list[dict]) -> dict:
        if not book_metadata:
            print("⚠️ No book metadata provided")
            return {"error": "책 정보가 제공되지 않았습니다."}

        selected = book_metadata[0]
        title = selected.get("title", "")
        author = selected.get("authors", "")
        description = selected.get("description", "")

        print(f"📚 Starting chat for book: {title}")

        system_msg = {"role": "system", "content": "당신은 책을 잘 아는 친절한 도우미입니다."}
        user_msg = {"role": "user", "content": self.generate_prompt(title, author, description)}
        messages = [system_msg, user_msg]

        clova_response = self.call_clova(messages)
        self.save_user_history(selected, clova_response)

        return {
            "response": clova_response,
            "session": messages + [{"role": "assistant", "content": clova_response}]
        }


    def followup_chat(self, session_messages: list[dict], user_input: str) -> dict:
        print(f"➡️ User follow-up: {user_input}")

        cleaned_session = [
            msg for msg in session_messages
            if isinstance(msg, dict) and msg.get("role") in {"user", "assistant", "system"} and msg.get("content")
        ]

        cleaned_session.append({"role": "user", "content": user_input})

        clova_response = self.call_clova(cleaned_session)

        cleaned_session.append({"role": "assistant", "content": clova_response})

        print("✅ Follow-up complete")

        return {
            "response": clova_response,
            "session": cleaned_session
        }

