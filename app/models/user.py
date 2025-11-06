from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class UserModel(Base):
    __tablename__ = "user_mobile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    phone = Column(String(11), nullable=False)
    address = relationship("AddressModel", uselist=False, back_populates="user")
    results = relationship("ResultModel", back_populates="user")


class AddressModel(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_mobile.id"), unique=True)
    cep = Column(String(8), nullable=False)
    street = Column(String(255), nullable=False)
    number = Column(Integer, nullable=False)
    neighborhood = Column(String(100), nullable=False)
    complement = Column(String(10), nullable=True)
    city = Column(String(100), nullable=False)
    lat = Column(String(50), nullable=False)
    lng = Column(String(50), nullable=False)
    user = relationship("UserModel", back_populates="address")
