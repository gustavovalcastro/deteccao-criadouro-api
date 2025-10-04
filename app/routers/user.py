from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import User, UserCreate, UserLogin, UserUpdate, UserLoginResponse
from app.services.user_service import UserService, UserEmailAlreadyExists
from app.database import get_db

router = APIRouter(prefix="/user", tags=["user"])

# ------------------------- POST -------------------------------

# Endpoint POST - Create User
@router.post("/createUser", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    address = user.address
    try:
        return UserService.create_user(db, user, address)
    except UserEmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        ) from None

#Endpoint POST - User Login
@router.post("/login", response_model=UserLoginResponse)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = UserService.authenticate(db, user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "error", "error": "Invalid email or password"}
        )
    return {
        "message": "success",
        "profile": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    }

# ------------------------- GET -------------------------------

# Endpoint GET - List all users
@router.get("/getAllUsers", response_model=list[User])
def list_users(db: Session = Depends(get_db)):
    return UserService.list_users(db)

# Endpoint GET - Get user by id
@router.get("/getUser/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# ------------------------- PUT -------------------------------

# Endpoint PUT - Update user
@router.put("/updateUser/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = UserService.update_user(db, user_id, user_update)
    except UserEmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        ) from None

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# ------------------------- DELETE -------------------------------

# Endpoint DELETE - Delete user
@router.delete("/deleteUser/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = UserService.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}