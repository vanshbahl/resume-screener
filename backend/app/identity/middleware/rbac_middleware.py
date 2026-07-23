from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.identity.models.user import User
from app.identity.middleware.auth_middleware import get_current_user
from app.identity.middleware.org_middleware import get_current_organization_id
from app.identity.services.authorization_service import AuthorizationService

class RequiresPermission:
    def __init__(self, permission: str):
        self.permission = permission
        
    def __call__(self, 
                 user: User = Depends(get_current_user),
                 org_id: int = Depends(get_current_organization_id),
                 db: Session = Depends(get_db)):
        
        auth_service = AuthorizationService(db)
        has_perm = auth_service.has_permission(user.id, org_id, self.permission)
        
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.permission}"
            )
        return True
