from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as DBSession
from app.core.database import get_db
from app.identity.security.jwt import decode_access_token
from app.identity.models.user import User
from app.identity.models.auth import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    db: DBSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception
    user_id = int(sub)
    jti: str = payload.get("jti")
    if jti is None:
        raise credentials_exception
        
    # Validate session exists and is not revoked
    session = db.query(Session).filter(Session.token_jti == jti, Session.is_revoked == False).first()
    if not session:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise credentials_exception
        
    return user
