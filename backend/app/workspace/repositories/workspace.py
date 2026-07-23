from typing import List, Optional
from sqlalchemy.orm import Session
from app.workspace.models.workspace import SavedSearch, Favorite, Preference, Notification
from app.workspace.schemas.workspace import SavedSearchCreate, SavedSearchUpdate, FavoriteCreate, NotificationCreate, PreferenceUpdate

class WorkspaceRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Saved Searches ---
    def get_saved_searches(self, user_id: str) -> List[SavedSearch]:
        return self.db.query(SavedSearch).filter(SavedSearch.user_id == user_id).all()

    def get_saved_search(self, search_id: str) -> Optional[SavedSearch]:
        return self.db.query(SavedSearch).filter(SavedSearch.id == search_id).first()

    def create_saved_search(self, user_id: str, search: SavedSearchCreate) -> SavedSearch:
        db_search = SavedSearch(
            user_id=user_id,
            name=search.name,
            search_type=search.search_type,
            criteria=search.criteria
        )
        self.db.add(db_search)
        self.db.commit()
        self.db.refresh(db_search)
        return db_search

    def update_saved_search(self, search_id: str, search: SavedSearchUpdate) -> Optional[SavedSearch]:
        db_search = self.get_saved_search(search_id)
        if not db_search:
            return None
        
        if search.name is not None:
            db_search.name = search.name
        if search.criteria is not None:
            db_search.criteria = search.criteria
            
        self.db.commit()
        self.db.refresh(db_search)
        return db_search
        
    def delete_saved_search(self, search_id: str) -> bool:
        db_search = self.get_saved_search(search_id)
        if db_search:
            self.db.delete(db_search)
            self.db.commit()
            return True
        return False

    # --- Favorites ---
    def get_favorites(self, user_id: str, entity_type: Optional[str] = None) -> List[Favorite]:
        query = self.db.query(Favorite).filter(Favorite.user_id == user_id)
        if entity_type:
            query = query.filter(Favorite.entity_type == entity_type)
        return query.all()

    def add_favorite(self, user_id: str, favorite: FavoriteCreate) -> Favorite:
        # Check if already exists
        existing = self.db.query(Favorite).filter(
            Favorite.user_id == user_id, 
            Favorite.entity_type == favorite.entity_type,
            Favorite.entity_id == favorite.entity_id
        ).first()
        if existing:
            return existing

        db_fav = Favorite(
            user_id=user_id,
            entity_type=favorite.entity_type,
            entity_id=favorite.entity_id,
            folder=favorite.folder
        )
        self.db.add(db_fav)
        self.db.commit()
        self.db.refresh(db_fav)
        return db_fav
        
    def remove_favorite(self, user_id: str, entity_type: str, entity_id: str) -> bool:
        db_fav = self.db.query(Favorite).filter(
            Favorite.user_id == user_id, 
            Favorite.entity_type == entity_type,
            Favorite.entity_id == entity_id
        ).first()
        if db_fav:
            self.db.delete(db_fav)
            self.db.commit()
            return True
        return False

    # --- Preferences ---
    def get_preferences(self, user_id: str) -> Preference:
        pref = self.db.query(Preference).filter(Preference.user_id == user_id).first()
        if not pref:
            pref = Preference(user_id=user_id, settings={})
            self.db.add(pref)
            self.db.commit()
            self.db.refresh(pref)
        return pref

    def update_preferences(self, user_id: str, prefs: PreferenceUpdate) -> Preference:
        db_pref = self.get_preferences(user_id)
        
        # Merge settings
        current_settings = db_pref.settings or {}
        current_settings.update(prefs.settings)
        db_pref.settings = current_settings
        
        self.db.commit()
        self.db.refresh(db_pref)
        return db_pref

    # --- Notifications ---
    def get_notifications(self, user_id: str, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read.is_(False))
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def create_notification(self, notif: NotificationCreate) -> Notification:
        db_notif = Notification(
            user_id=notif.user_id,
            type=notif.type,
            content=notif.content
        )
        self.db.add(db_notif)
        self.db.commit()
        self.db.refresh(db_notif)
        return db_notif

    def mark_notification_read(self, notification_id: str) -> bool:
        db_notif = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if db_notif:
            db_notif.is_read = True
            self.db.commit()
            return True
        return False
