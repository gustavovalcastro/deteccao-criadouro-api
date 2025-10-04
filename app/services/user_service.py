from sqlalchemy.orm import Session
import bcrypt
from app.models.user import UserModel, AddressModel
from app.schemas.user import UserCreate, AddressCreate, UserLogin, UserUpdate


class UserEmailAlreadyExists(Exception):
    """Raised when trying to use an e-mail that is already registered for another user."""


class UserInvalidCredentials(Exception):
    """Raised when a password check fails."""


class UserService:
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
    def create_user(db: Session, user: UserCreate, address: AddressCreate) -> UserModel:
        existing = db.query(UserModel).filter(UserModel.email == user.email).first()
        if existing:
            raise UserEmailAlreadyExists()

        hashed_password = UserService._hash_password(user.password)

        db_user = UserModel(
            name=user.name,
            email=user.email,
            password=hashed_password,
            phone=user.phone
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        db_address = AddressModel(
            user_id=db_user.id,
            cep=address.cep,
            street=address.street,
            number=address.number,
            neighborhood=address.neighborhood,
            complement=address.complement,
            city=address.city,
            lat=address.lat,
            lng=address.lng
        )
        db.add(db_address)
        db.commit()
        db.refresh(db_address)
        db.refresh(db_user)

        return db_user

    @staticmethod
    def list_users(db: Session):
        return db.query(UserModel).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(UserModel).filter(UserModel.id == user_id).first()

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate):
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return None

        if user_update.email is not None and user_update.email != user.email:
            existing = db.query(UserModel).filter(UserModel.email == user_update.email).first()
            if existing:
                raise UserEmailAlreadyExists()

        for attr in ("name", "email", "phone"):
            value = getattr(user_update, attr)
            if value is not None:
                setattr(user, attr, value)

        if user_update.password is not None:
            user.password = UserService._hash_password(user_update.password)

        if user_update.address is not None and user.address is not None:
            address_data = user_update.address
            address = user.address
            for attr in ("cep", "street", "number", "neighborhood", "complement", "city", "lat", "lng"):
                value = getattr(address_data, attr)
                if value is not None:
                    setattr(address, attr, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return False

        if user.address:
            db.delete(user.address)
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def authenticate(db: Session, login: UserLogin):
        user = db.query(UserModel).filter(UserModel.email == login.email).first()
        if not user:
            return None
        if not UserService._verify_password(login.password, user.password):
            return None
        return user