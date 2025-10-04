from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.userPortal import (
    UserPortalCreate,
    UserPortal,
    UserPortalLogin,
    UserPortalUpdate,
    UserPortalLoginResponse,
)
from app.services.userPortal_service import (
    UserPortalService,
    UserPortalEmailAlreadyExists,
)
from app.database import get_db

router = APIRouter(prefix="/userPortal", tags=["userPortal"])


# ------------------------- POST -------------------------------

@router.post("/createUserPortal", response_model=UserPortalLoginResponse)
def create_user_portal(user: UserPortalCreate, db: Session = Depends(get_db)):
    try:
        user_portal = UserPortalService.create_user_portal(db, user)
    except UserPortalEmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        ) from None

    return {
        "message": "success",
        "profile": {
            "id": user_portal.id,
            "name": user_portal.name,
            "email": user_portal.email,
        }
    }


@router.post("/login", response_model=UserPortalLoginResponse)
def login(user_login: UserPortalLogin, db: Session = Depends(get_db)):
    user_portal = UserPortalService.authenticate(db, user_login)
    if not user_portal:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "error", "error": "Invalid email or password"}
        )
    return {
        "message": "success",
        "profile": {
            "id": user_portal.id,
            "name": user_portal.name,
            "email": user_portal.email,
        }
    }


# ------------------------- GET -------------------------------

@router.get("/getAllUserPortals", response_model=list[UserPortal])
def list_user_portals(db: Session = Depends(get_db)):
    return UserPortalService.list_user_portals(db)


@router.get("/getUserPortal/{user_portal_id}", response_model=UserPortal)
def get_user_portal(user_portal_id: int, db: Session = Depends(get_db)):
    user_portal = UserPortalService.get_user_portal_by_id(db, user_portal_id)
    if not user_portal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portal user not found"
        )
    return user_portal


# ------------------------- PUT -------------------------------

@router.put("/updateUserPortal/{user_portal_id}", response_model=UserPortal)
def update_user_portal(
    user_portal_id: int,
    user_update: UserPortalUpdate,
    db: Session = Depends(get_db)
):
    try:
        user_portal = UserPortalService.update_user_portal(db, user_portal_id, user_update)
    except UserPortalEmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        ) from None

    if not user_portal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portal user not found"
        )
    return user_portal


# ------------------------- DELETE -------------------------------

@router.delete("/deleteUserPortal/{user_portal_id}")
def delete_user_portal(user_portal_id: int, db: Session = Depends(get_db)):
    deleted = UserPortalService.delete_user_portal(db, user_portal_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portal user not found"
        )
    return {"message": "Portal user deleted successfully"}