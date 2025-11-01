from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums.result import ResultType, ResultStatus


class ResultModel(Base):
    __tablename__ = "result"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaign.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    original_image = Column(String, nullable=False)
    result_image = Column(String, nullable=True)
    type = Column(Enum(ResultType, name="result_type"), nullable=False)
    status = Column(Enum(ResultStatus, name="result_status"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    object_count = Column(Integer, nullable=True)
    feedback_like = Column(Boolean, default=False, nullable=False)
    feedback_comment = Column(String, nullable=True)

    campaign = relationship("CampaignModel", back_populates="results")
    user = relationship("UserModel", back_populates="results")
