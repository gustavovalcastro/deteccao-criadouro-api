from pydantic import BaseModel, EmailStr
from typing import Optional


class UserPortalCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    city: str


class UserPortalUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    city: Optional[str] = None


class UserPortalLogin(BaseModel):
    email: EmailStr
    password: str


class UserPortal(BaseModel):
    id: int
    name: str
    email: EmailStr
    city: str

    class Config:
        from_attributes = True


class UserPortalSummary(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserPortalLoginResponse(BaseModel):
    message: str
    profile: UserPortalSummary
