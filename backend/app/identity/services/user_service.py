from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.identity.models.user import User
from app.identity.schemas.user import UserCreate, UserUpdate
from app.identity.security.password import get_password_hash

class UserService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()
        
    def create_user(self, user_in: UserCreate) -> User:
        existing = self.get_by_email(user_in.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
            
        hashed_password = get_password_hash(user_in.password)
        
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            organization_id=user_in.organization_id
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
