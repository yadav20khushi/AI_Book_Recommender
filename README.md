# Module-wise updates/documentation
**module: apps/config_loader/..**
- **config_parser.py:**
  - written proper parser logic (i.e., to convert JSON to Python dictionary)
  - Handled exceptions like missing key, module not found, and invalid JSON
- **config_store.py:**
  - wrote code to make the parsing logic accessible globally
- **unittest: *performed successful tests in python manage.py shell:***
  - **Test 1**:<br>
   -->from apps.config_loader.config_store import get config<br>
   -->config = get_config()<br>
   -->print(config)<br>
   **result**: {'library_id': 'SEOUL001', 'enable_media': 'True', 'theme_class': 'blue-theme', 'naru_region_code': 'KR-11'}<br>
  - **Test 2**:<br>
   -->from apps.config_loader.config_store import get config<br>
   -->config = get_config()<br>
   -->print(config)<br>
   **result**: 'Missing required config keys: library_id'<br>
- **✅*Intern Focus: Write config parsing logic. Test with sample JSONs.* <br>**

**module: apps/recommendations/..**
- **recommendation.py:**
  - built_prompt - develops multiple prompts to send to Clova
  - call_clova - returns a mocked response
  - parse_response - strips book titles and returns as a list
  - get_recommendations - simulates entire process and stores log data in DB
- **models.py:**
  - PromptLog - stores prompt, response, and time log
- **unittest: *performed successful tests in python manage.py shell:***
  - **Test 1**: *to check multiple prompt templates*<br>
   -->from apps.recommendations.recommendation import built_prompt<br>
   -->for _ in range(5):                                           
      .....print(built_prompt("fantasy", "children"))<br>
   **result**: What are 5 highly-rated fantasy books for children readers? What are 5 highly-rated fantasy books for children readers? Can you suggest five fantasy books for someone in the children category? Give me a list of 5 fantasy books that are great for children. Recommend 5 fantasy books suitable for children.
  - **Test 2**: *to validate clova API call integration*<br>
    -->from apps.recommendations.recommendation import get_recommendations<br>
    -->books = get_recommendations('fantasy','children')<br>
    -->print(books)<br>
  **result**: ['The Hobbit by J.R.R. Tolkien', 'Percy Jackson and the Olympians by Rick Riordan', "Harry Potter and the Sorcerer's Stone by J.K. Rowling", 'Eragon by Christopher Paolini', 'The                     Chronicles of Narnia by C.S. Lewis']<br>
   --> PromptLog.objects.all()<br>
  **result**: <QuerySet [<PromptLog: PromptLog (2025-05-18 07:40:31.162822+00:00): I'm looking for fantasy books ...>, <PromptLog: PromptLog (2025-05-18 07:47:11.744921+00:00): What are 5 highly-                 rated fantas...>]>
- **Error**: RuntimeError: Model class apps.recommendations.models.PromptLog doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.
   - Cause:
      - This error occurred because Django was not recognizing the recommendations app properly.
      - The root cause was related to the app not being correctly registered or an issue with migrations/state.
    
   - Solution:
      - Ensured apps.recommendations was correctly added to INSTALLED_APPS in settings.py (using the dotted path).
      - Deleted all .pyc files and __pycache__ folders to clear any stale compiled files.
      - Created migrations multiple times (0001_initial.py, then 0002_alter_promptlog_created_at.py, finally 0003_alter_promptlog_created_at.py) to sync model changes.
      - Fixed the DateTimeField default by using default=timezone.now without parentheses to avoid setting a fixed datetime.
      - Finally ran python manage.py migrate successfully without errors.
    
- **Future note**: When integrating APIs, we would have to optimize the call_clova function so that it efficiently handles edge cases (e.g., empty responses, errors, retries), Be optimized for latency and reliability, possibly be wrapped in async or caching logic depending on usage volume.
- **✅*Intern Focus: Create and test multiple prompt templates. Validate Clova API call integration.* <br>**



  

