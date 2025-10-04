from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.result import ResultModel
from app.models.campaign import CampaignModel
from app.models.user import UserModel
from app.models.enums.result import ResultStatus
from app.schemas.result import ResultCreate


class CampaignNotFoundError(Exception):
    """Raised when the requested campaign does not exist."""


class UserNotFoundError(Exception):
    """Raised when the user does not exist."""


class ResultService:

    @staticmethod
    def create_result(db: Session, payload: ResultCreate) -> ResultModel:
        if payload.campaignId is not None:
            campaign = (
                db.query(CampaignModel)
                .filter(CampaignModel.id == payload.campaignId)
                .first()
            )
            if not campaign:
                raise CampaignNotFoundError()

        user: Optional[UserModel] = None
        if payload.userId is not None:
            user = db.query(UserModel).filter(UserModel.id == payload.userId).first()
            if not user:
                raise UserNotFoundError()

        feedback_like = payload.feedback.like if payload.feedback else False
        feedback_comment = payload.feedback.comment if payload.feedback else None

        result = ResultModel(
            campaign_id=payload.campaignId,
            user_id=user.id if user else None,
            original_image=payload.originalImage,
            result_image=payload.resultImage,
            type=payload.type,
            status=payload.status,
            created_at=datetime.utcnow(),
            feedback_like=feedback_like,
            feedback_comment=feedback_comment,
        )

        if user:
            result.user = user

        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    @staticmethod
    def get_result_by_id(db: Session, result_id: int) -> ResultModel | None:
        return db.query(ResultModel).filter(ResultModel.id == result_id).first()

    @staticmethod
    def update_result_status(
        db: Session,
        result_id: int,
        status,
    ) -> tuple[ResultModel | None, str | None]:
        result = ResultService.get_result_by_id(db, result_id)
        if result is None:
            return None, "RESULT_NOT_FOUND"

        try:
            new_status = status if isinstance(status, ResultStatus) else ResultStatus(status)
        except ValueError:
            return None, "INVALID_STATUS"

        result.status = new_status

        db.commit()
        db.refresh(result)
        return result, None

    @staticmethod
    def get_results_by_user(db: Session, user_id: int) -> list[ResultModel]:
        return (
            db.query(ResultModel)
            .filter(ResultModel.user_id == user_id)
            .all()
        )