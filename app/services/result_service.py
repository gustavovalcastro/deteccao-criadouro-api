from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.result import ResultModel
from app.models.campaign import CampaignModel
from app.models.user import UserModel, AddressModel
from app.models.enums.result import ResultStatus, ResultType


class CampaignNotFoundError(Exception):
    """Raised when the requested campaign does not exist."""


class UserNotFoundError(Exception):
    """Raised when the user does not exist."""


class ResultService:

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
    def update_result_image_and_status(
        db: Session,
        result_id: int,
        result_image: str,
        status,
        object_count: Optional[int] = None,
    ) -> tuple[ResultModel | None, str | None]:
        result = ResultService.get_result_by_id(db, result_id)
        if result is None:
            return None, "RESULT_NOT_FOUND"

        try:
            new_status = status if isinstance(status, ResultStatus) else ResultStatus(status)
        except ValueError:
            return None, "INVALID_STATUS"

        # Only allow processing or failed statuses for result image updates
        if new_status not in [ResultStatus.finished, ResultStatus.failed]:
            return None, "INVALID_STATUS_FOR_IMAGE_UPDATE"

        # If status is finished, object_count must be provided
        if new_status == ResultStatus.finished and object_count is None:
            return None, "OBJECT_COUNT_REQUIRED_FOR_FINISHED"

        result.result_image = result_image
        result.status = new_status
        result.object_count = object_count
        
        # Set processed_at timestamp when status is finished
        if new_status == ResultStatus.finished:
            result.processed_at = datetime.utcnow()

        db.commit()
        db.refresh(result)
        return result, None

    @staticmethod
    def update_result_feedback(
        db: Session,
        result_id: int,
        like: bool,
        comment: Optional[str] = None,
    ) -> tuple[ResultModel | None, str | None]:
        result = ResultService.get_result_by_id(db, result_id)
        if result is None:
            return None, "RESULT_NOT_FOUND"

        result.feedback_like = like
        result.feedback_comment = comment

        db.commit()
        db.refresh(result)
        return result, None

    @staticmethod
    def delete_result(db: Session, result_id: int) -> tuple[bool, str | None]:
        """
        Delete a result by ID.
        
        Args:
            db: Database session
            result_id: ID of the result to delete
            
        Returns:
            Tuple of (success: bool, error: str | None)
        """
        result = ResultService.get_result_by_id(db, result_id)
        if result is None:
            return False, "RESULT_NOT_FOUND"
        
        db.delete(result)
        db.commit()
        return True, None

    @staticmethod
    def get_all_results(db: Session) -> list[ResultModel]:
        return db.query(ResultModel).all()

    @staticmethod
    def get_results_by_user(db: Session, user_id: int) -> list[ResultModel]:
        return (
            db.query(ResultModel)
            .filter(ResultModel.user_id == user_id)
            .all()
        )

    @staticmethod
    def create_result_from_upload(
        db: Session,
        image_url: str,
        user_id: int,
        campaign_id: Optional[int] = None,
        result_type: Optional[ResultType] = None,
        lat: Optional[str] = None,
        lng: Optional[str] = None,
    ) -> ResultModel:
        """
        Create a result from an uploaded image.
        
        Args:
            db: Database session
            image_url: The GCP Storage URL of the uploaded image
            user_id: The ID of the user uploading the image
            campaign_id: Optional campaign ID
            result_type: Optional result type, defaults to ResultType.terreno
            lat: Optional latitude coordinate
            lng: Optional longitude coordinate
            
        Returns:
            The created ResultModel
            
        Raises:
            UserNotFoundError: If the user doesn't exist
            CampaignNotFoundError: If the campaign doesn't exist
        """
        # Verify user exists
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise UserNotFoundError()

        # Verify campaign exists if provided
        if campaign_id is not None:
            campaign = (
                db.query(CampaignModel)
                .filter(CampaignModel.id == campaign_id)
                .first()
            )
            if not campaign:
                raise CampaignNotFoundError()

        # Set defaults
        if result_type is None:
            result_type = ResultType.terreno

        # If coordinates are not provided, use user's address coordinates
        if lat is None or lng is None:
            address = db.query(AddressModel).filter(AddressModel.user_id == user_id).first()
            if address:
                lat = address.lat if lat is None else lat
                lng = address.lng if lng is None else lng

        result = ResultModel(
            campaign_id=campaign_id,
            user_id=user_id,
            original_image=image_url,
            result_image=None,
            type=result_type,
            status=ResultStatus.processing,
            created_at=datetime.utcnow(),
            feedback_like=None,
            feedback_comment=None,
            lat=lat,
            lng=lng,
        )

        result.user = user

        db.add(result)
        db.commit()
        db.refresh(result)
        return result