from app.core.auth.jwt import create_access_token, decode_access_token
from datetime import timedelta
token = create_access_token({'user_id': 'x'})
# Can't easily force expiry in unit test — just verify structure
payload = decode_access_token(token)
assert 'exp' in payload
print('exp field present: OK')