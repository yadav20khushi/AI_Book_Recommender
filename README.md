
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
