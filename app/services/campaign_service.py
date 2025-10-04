from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.campaign import CampaignModel
from app.models.userPortal import UserPortalModel
from app.models.user import UserModel
from app.schemas.campaign import CampaignCreate, CampaignUpdate


class CampaignService:

    @staticmethod
    def create_campaign(db: Session, campaign_data: CampaignCreate) -> CampaignModel:
        campaign = CampaignModel(
            title=campaign_data.title,
            description=campaign_data.description,
            city=campaign_data.city,
            campaignInfos=campaign_data.campaignInfos,
            instructionInfos=campaign_data.instructionInfos,
            created_at=campaign_data.created_at or datetime.utcnow(),
            finish_at=campaign_data.finish_at,
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    @staticmethod
    def get_campaign_by_id(db: Session, campaign_id: int) -> CampaignModel | None:
        return db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()

    @staticmethod
    def get_campaigns_by_city(db: Session, city: str) -> List[CampaignModel]:
        return db.query(CampaignModel).filter(CampaignModel.city == city).all()

    @staticmethod
    def get_campaigns_for_user_portal(
        db: Session, user_portal_id: int
    ) -> Tuple[List[CampaignModel] | None, str | None, str | None]:
        user_portal = (
            db.query(UserPortalModel)
            .filter(UserPortalModel.id == user_portal_id)
            .first()
        )
        if not user_portal:
            return None, None, "USER_PORTAL_NOT_FOUND"

        city = user_portal.city
        campaigns = CampaignService.get_campaigns_by_city(db, city)
        return campaigns, city, None

    @staticmethod

    @staticmethod
    def get_all_campaigns(db: Session) -> List[CampaignModel]:
        return db.query(CampaignModel).all()
    def get_campaigns_for_user(
        db: Session, user_id: int
    ) -> Tuple[List[CampaignModel] | None, str | None, str | None]:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return None, None, "USER_NOT_FOUND"
        if not user.address:
            return None, None, "ADDRESS_NOT_FOUND"

        city = user.address.city
        campaigns = CampaignService.get_campaigns_by_city(db, city)
        return campaigns, city, None

    @staticmethod
    def update_campaign(
        db: Session, campaign_id: int, campaign_update: CampaignUpdate
    ) -> CampaignModel | None:
        campaign = db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
        if not campaign:
            return None

        mapping = {
            "title": campaign_update.title,
            "description": campaign_update.description,
            "city": campaign_update.city,
            "campaignInfos": campaign_update.campaignInfos,
            "instructionInfos": campaign_update.instructionInfos,
            "created_at": campaign_update.created_at,
            "finish_at": campaign_update.finish_at,
        }

        for attr, value in mapping.items():
            if value is not None:
                setattr(campaign, attr, value)

        db.commit()
        db.refresh(campaign)
        return campaign

    @staticmethod
    def delete_campaign(db: Session, campaign_id: int) -> bool:
        campaign = db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
        if not campaign:
            return False

        db.delete(campaign)
        db.commit()
        return True