from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.identity.models.user import User
from app.identity.middleware.auth_middleware import get_current_user

def get_current_organization_id(request: Request, user: User = Depends(get_current_user)) -> int:
    # 1. Try to get from header
    org_id_str = request.headers.get("X-Organization-Id")
    if org_id_str and org_id_str.isdigit():
        org_id = int(org_id_str)
        # Ensure user belongs to this org (in a multi-org setup, we'd check memberships)
        # For our MVP, User is strictly tied to one Organization directly via user.organization_id
        if user.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this organization")
        return org_id
        
    # 2. Fallback to user's primary organization
    if user.organization_id:
        return user.organization_id
        
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization context missing")
