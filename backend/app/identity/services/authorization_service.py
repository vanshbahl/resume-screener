from typing import List, Set
from sqlalchemy.orm import Session
from app.identity.models.user import User, Membership
from app.identity.models.rbac import Role, Permission, RolePermission

class AuthorizationService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_user_permissions(self, user_id: int, organization_id: int) -> Set[str]:
        # 1. Get all roles for the user in this organization via memberships
        memberships = self.db.query(Membership).filter(
            Membership.user_id == user_id
        ).all()
        
        # Filter for organization context (since roles are tied to orgs)
        role_ids = []
        for m in memberships:
            role = self.db.query(Role).filter(Role.id == m.role_id, Role.organization_id == organization_id).first()
            if role:
                role_ids.append(role.id)
                
        if not role_ids:
            return set()
            
        # 2. Get all permissions linked to these roles
        role_permissions = self.db.query(RolePermission).filter(
            RolePermission.role_id.in_(role_ids)
        ).all()
        
        permission_ids = [rp.permission_id for rp in role_permissions]
        
        if not permission_ids:
            return set()
            
        permissions = self.db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        return set([p.name for p in permissions])
        
    def has_permission(self, user_id: int, organization_id: int, required_permission: str) -> bool:
        # Resolve all permissions (cached ideally, but computed here for MVP)
        user_permissions = self.get_user_permissions(user_id, organization_id)
        
        # Handle exact match
        if required_permission in user_permissions:
            return True
            
        # Handle wildcard matches (e.g. user has 'job.*', requires 'job.read')
        parts = required_permission.split('.')
        if len(parts) > 1:
            wildcard = f"{parts[0]}.*"
            if wildcard in user_permissions:
                return True
                
        # Handle super admin wildcard
        if "*" in user_permissions:
            return True
            
        return False
