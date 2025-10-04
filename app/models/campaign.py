from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.database import Base


class CampaignModel(Base):
    __tablename__ = "campaign"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    campaignInfos = Column(JSON, nullable=True)
    instructionInfos = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finish_at = Column(DateTime, nullable=True)
    city = Column(String, nullable=False)
    results = relationship(
        "ResultModel",
        back_populates="campaign",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )