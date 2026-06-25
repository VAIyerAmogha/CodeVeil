
from app.ingestion.cloner import clone_repository
from app.ingestion.language_detector import detect_language, is_ast_supported
from app.services.github import fetch_repo_metadata

# Test cloner
path = clone_repository('https://github.com/tiangolo/fastapi')
print('cloned to:', path)

# Test language detector
print(detect_language('main.py'))        # Python
print(is_ast_supported('Python'))        # True
print(is_ast_supported('Go'))            # False

# Test GitHub service
meta = fetch_repo_metadata('https://github.com/tiangolo/fastapi')
print(meta['stars'], meta['primary_language'])

# Also test rejection:
# Expect: CloneError raised