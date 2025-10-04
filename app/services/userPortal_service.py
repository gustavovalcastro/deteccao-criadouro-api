from sqlalchemy.orm import Session
import bcrypt
from app.models.userPortal import UserPortalModel
from app.schemas.userPortal import UserPortalCreate, UserPortalUpdate, UserPortalLogin


class UserPortalEmailAlreadyExists(Exception):
    """Raised when the e-mail is already registered for another portal user."""


class UserPortalService:
    @staticmethod
    def _hash_password(plain_password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except ValueError:
            return False

    @staticmethod
    def create_user_portal(db: Session, user: UserPortalCreate) -> UserPortalModel:
        existing = (
            db.query(UserPortalModel)
            .filter(UserPortalModel.email == user.email)
            .first()
        )
        if existing:
            raise UserPortalEmailAlreadyExists()

        hashed_password = UserPortalService._hash_password(user.password)

        user_portal = UserPortalModel(
            name=user.name,
            email=user.email,
            password=hashed_password,
            city=user.city
        )
        db.add(user_portal)
        db.commit()
        db.refresh(user_portal)
        return user_portal

    @staticmethod
    def list_user_portals(db: Session):
        return db.query(UserPortalModel).all()

    @staticmethod
    def get_user_portal_by_id(db: Session, user_portal_id: int):
        return (
            db.query(UserPortalModel)
            .filter(UserPortalModel.id == user_portal_id)
            .first()
        )

    @staticmethod
    def update_user_portal(db: Session, user_portal_id: int, user_update: UserPortalUpdate):
        user_portal = (
            db.query(UserPortalModel).filter(UserPortalModel.id == user_portal_id).first()
        )
        if not user_portal:
            return None

        if user_update.email is not None and user_update.email != user_portal.email:
            existing = (
                db.query(UserPortalModel)
                .filter(UserPortalModel.email == user_update.email)
                .first()
            )
            if existing:
                raise UserPortalEmailAlreadyExists()

        if user_update.password is not None:
            user_portal.password = UserPortalService._hash_password(user_update.password)

        for attr in ("name", "email", "city"):
            value = getattr(user_update, attr)
            if value is not None:
                setattr(user_portal, attr, value)

        db.commit()
        db.refresh(user_portal)
        return user_portal

    @staticmethod
    def delete_user_portal(db: Session, user_portal_id: int) -> bool:
        user_portal = (
            db.query(UserPortalModel).filter(UserPortalModel.id == user_portal_id).first()
        )
        if not user_portal:
            return False

        db.delete(user_portal)
        db.commit()
        return True

    @staticmethod
    def authenticate(db: Session, login: UserPortalLogin):
        user_portal = (
            db.query(UserPortalModel).filter(UserPortalModel.email == login.email).first()
        )
        if not user_portal:
            return None
        if not UserPortalService._verify_password(login.password, user_portal.password):
            return None
        return user_portal