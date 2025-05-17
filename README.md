# Module-wise updates/documentation
module: apps/config_loader
- config_parser.py: 
  - written proper parser logic (i.e., to convert JSON to Python dictionary)
  - Handled exceptions like missing key, module not found, and invalid JSON
- config_store.py:
  - wrote code to make the parsing logic accessible globally
- unittest: performed successful tests in python manage.py shell:
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
- ✅*Intern Focus: Write config parsing logic. Test with sample JSONs.*
