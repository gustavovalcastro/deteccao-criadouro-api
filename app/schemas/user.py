from pydantic import BaseModel, EmailStr
from typing import Optional


class AddressCreate(BaseModel):
    cep: str
    street: str
    number: int
    neighborhood: str
    complement: Optional[str] = None
    city: str
    lat: str
    lng: str

    class Config:
        json_schema_extra = {
            "example": {
                "cep": "01001000",
                "street": "Praca da Se",
                "number": 1,
                "neighborhood": "Se",
                "complement": "lado impar",
                "city": "Sao Paulo",
                "lat": "-23.550520",
                "lng": "-46.633308"
            }
        }


class AddressUpdate(BaseModel):
    cep: Optional[str] = None
    street: Optional[str] = None
    number: Optional[int] = None
    neighborhood: Optional[str] = None
    complement: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[str] = None
    lng: Optional[str] = None


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    address: AddressCreate

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Maria Silva",
                "email": "maria@example.com",
                "password": "senhaSegura123",
                "phone": "11999999999",
                "address": {
                    "cep": "01001000",
                    "street": "Praca da Se",
                    "number": 1,
                    "neighborhood": "Se",
                    "complement": "lado impar",
                    "city": "Sao Paulo",
                    "lat": "-23.550520",
                    "lng": "-46.633308"
                }
            }
        }


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[AddressUpdate] = None


class Address(BaseModel):
    id: int
    user_id: int
    cep: str
    street: str
    number: int
    neighborhood: str
    complement: Optional[str] = None
    city: str
    lat: str
    lng: str

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    address: Address

    class Config:
        from_attributes = True


class UserSummary(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    message: str
    profile: UserSummary
