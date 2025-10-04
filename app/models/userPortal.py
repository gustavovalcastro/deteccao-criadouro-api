from sqlalchemy import Column, Integer, String
from app.database import Base

class UserPortalModel(Base):
    __tablename__ = "user_portal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    city = Column(String, nullable=False)
