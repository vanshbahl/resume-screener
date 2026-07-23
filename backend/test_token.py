import sys
sys.path.append('.')
from app.identity.security.jwt import create_access_token

token = create_access_token({"sub": 1})
print(f"Token type: {type(token)}")
print(f"Token: {token}")
