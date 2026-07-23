from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.identity.models.organization import Organization, OrganizationSettings
from app.identity.schemas.organization import OrganizationCreate, OrganizationUpdate

class OrganizationService:
    def __init__(self, db: Session):
        self.db = db
        
    def get(self, org_id: int) -> Organization:
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        return org
        
    def create(self, org_in: OrganizationCreate) -> Organization:
        existing = self.db.query(Organization).filter(Organization.slug == org_in.slug).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization slug already exists")
            
        db_org = Organization(
            name=org_in.name,
            slug=org_in.slug
        )
        self.db.add(db_org)
        self.db.flush()
        
        db_settings = OrganizationSettings(organization_id=db_org.id)
        self.db.add(db_settings)
        self.db.commit()
        self.db.refresh(db_org)
        return db_org
