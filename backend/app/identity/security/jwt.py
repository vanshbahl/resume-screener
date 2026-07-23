from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import secrets
from app.core.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Require jti to identify specific token
    if "jti" not in to_encode:
        to_encode["jti"] = secrets.token_hex(16)
        
    to_encode.update({"exp": expire})
    print("ENCODING PAYLOAD:", to_encode)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded_token
    except jwt.PyJWTError as e:
        print(f"JWT DECODE ERROR: {e}")
        return None

def generate_refresh_token() -> str:
    return secrets.token_hex(32)
