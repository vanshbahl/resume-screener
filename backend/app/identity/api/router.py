from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.identity.schemas.auth import LoginRequest, TokenResponse
from app.identity.schemas.user import UserCreate, UserResponse
from app.identity.schemas.organization import OrganizationCreate, OrganizationResponse
from app.identity.services.authentication_service import AuthenticationService
from app.identity.services.user_service import UserService
from app.identity.services.organization_service import OrganizationService
from app.identity.middleware.auth_middleware import get_current_user
from app.identity.middleware.org_middleware import get_current_organization_id
from app.identity.middleware.rbac_middleware import RequiresPermission
from app.identity.models.user import User

router = APIRouter(prefix="/identity", tags=["Identity & Access Control"])

@router.post("/auth/login", response_model=TokenResponse)
def login(request_body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)
    # Simple IP grabbing for MVP
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    return auth_service.login(request_body, ip_address, user_agent)

@router.post("/auth/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import jwt
    from app.core.config import settings
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return {"status": "ok"}
        
    token = auth_header.split(" ")[1]
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    jti = decoded.get("jti")
    
    auth_service = AuthenticationService(db)
    auth_service.logout(jti)
    return {"status": "ok"}

@router.post("/organizations", response_model=OrganizationResponse)
def create_organization(
    org_in: OrganizationCreate, 
    db: Session = Depends(get_db)
):
    # Depending on setup, creating an org might be open or restricted to super admins
    org_service = OrganizationService(db)
    return org_service.create(org_in)

@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Enforce they can only get their own org for MVP
    if current_user.organization_id != org_id:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
    org_service = OrganizationService(db)
    return org_service.get(org_id)

@router.post("/users", response_model=UserResponse)
def create_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db)
    # For MVP, not protecting this endpoint strictly so we can bootstrap the first user
):
    user_service = UserService(db)
    return user_service.create_user(user_in)

@router.get("/users/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
