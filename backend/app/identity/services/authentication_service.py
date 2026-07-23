from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.identity.models.user import User
from app.identity.models.auth import Session as AuthSession, RefreshToken
from app.identity.schemas.auth import LoginRequest, TokenResponse
from app.identity.security.password import verify_password
from app.identity.security.jwt import create_access_token, generate_refresh_token
from datetime import datetime, timedelta
from app.core.config import settings

class AuthenticationService:
    def __init__(self, db: Session):
        self.db = db
        
    def login(self, request: LoginRequest, ip_address: str = None, user_agent: str = None) -> TokenResponse:
        user = self.db.query(User).filter(User.email == request.email).first()
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

        import secrets
        jti = secrets.token_hex(16)
        expire_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire_time = datetime.utcnow() + expire_delta
        
        # Create JWT Access Token
        access_token = create_access_token(
            data={"sub": str(user.id), "jti": jti},
            expires_delta=expire_delta
        )
        
        # Create Session
        db_session = AuthSession(
            user_id=user.id,
            token_jti=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expire_time
        )
        self.db.add(db_session)
        self.db.flush()
        
        # Create Refresh Token
        refresh_token_str = generate_refresh_token()
        db_refresh = RefreshToken(
            session_id=db_session.id,
            token=refresh_token_str,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(db_refresh)
        self.db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    def logout(self, jti: str):
        session = self.db.query(AuthSession).filter(AuthSession.token_jti == jti).first()
        if session:
            session.is_revoked = True
            for rt in session.refresh_tokens:
                rt.is_revoked = True
            self.db.commit()
