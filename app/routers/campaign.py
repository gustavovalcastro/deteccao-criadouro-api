from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.campaign import (
    CampaignResponse,
    Campaign,
    CampaignBasicResponse,
    UserCampaignsResponse,
    CampaignCreate,
    CampaignUpdate,
    CampaignResult,
    CampaignResultFeedback,
)
from app.services.campaign_service import CampaignService
from app.models.enums.result import ResultStatus
from app.database import get_db

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def _map_result(result_model) -> CampaignResult:
    feedback = CampaignResultFeedback(
        like=result_model.feedback_like,
        comment=result_model.feedback_comment,
    )
    return CampaignResult(
        id=result_model.id,
        originalImage=result_model.original_image,
        resultImage=result_model.result_image,
        type=result_model.type,
        status=result_model.status,
        feedback=feedback,
    )


def _map_campaign(
    campaign_model,
    *,
    only_user_id: int | None = None,
    include_results: bool = True,
) -> Campaign:
    results_model = []
    if include_results:
        results_model = campaign_model.results or []
        if only_user_id is not None:
            results_model = [result for result in results_model if result.user_id == only_user_id]

    results = [_map_result(result) for result in results_model]
    return Campaign(
        id=campaign_model.id,
        title=campaign_model.title,
        description=campaign_model.description,
        campaignInfos=campaign_model.campaignInfos,
        instructionInfos=campaign_model.instructionInfos,
        created_at=campaign_model.created_at,
        finish_at=campaign_model.finish_at,
        city=campaign_model.city,
        results=results,
    )


def _map_campaign_basic(campaign_model) -> CampaignBasicResponse:
    return CampaignBasicResponse(
        id=campaign_model.id,
        title=campaign_model.title,
        description=campaign_model.description,
        campaignInfos=campaign_model.campaignInfos,
        instructionInfos=campaign_model.instructionInfos,
        created_at=campaign_model.created_at,
        finish_at=campaign_model.finish_at,
        city=campaign_model.city,
    )


# ------------------------- POST -------------------------------

@router.post("/createCampaign", response_model=CampaignBasicResponse)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    created_campaign = CampaignService.create_campaign(db, campaign)
    return _map_campaign_basic(created_campaign)


# ------------------------- GET -------------------------------

@router.get("/getCampaign/{campaign_id}", response_model=Campaign)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = CampaignService.get_campaign_by_id(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return _map_campaign(campaign)


@router.get("/getCampaignByUser/{userId}", response_model=CampaignResponse)
def get_campaigns_for_user(userId: int, db: Session = Depends(get_db)):
    campaigns, _, error = CampaignService.get_campaigns_for_user(db, userId)
    if error == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if error == "ADDRESS_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereco do User not found",
        )

    campaigns_list = [_map_campaign(c, only_user_id=userId) for c in campaigns]
    return {"campaigns": campaigns_list}


@router.get("/getCampaignByUserPortal/{userPortalId}", response_model=CampaignResponse)
def get_campaigns_by_portal(userPortalId: int, db: Session = Depends(get_db)):
    campaigns, _, error = CampaignService.get_campaigns_for_user_portal(db, userPortalId)
    if error == "USER_PORTAL_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portal user not found",
        )

    campaigns_list = [_map_campaign_basic(c) for c in campaigns]
    return {"campaigns": campaigns_list}


@router.get("/getCampaignHome/{userId}", response_model=UserCampaignsResponse)
def get_campaign_home(userId: int, db: Session = Depends(get_db)):
    campaigns, _, error = CampaignService.get_campaigns_for_user(db, userId)
    if error == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if error == "ADDRESS_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endereco do User not found",
        )

    visualized_value = getattr(ResultStatus.visualized, "value", ResultStatus.visualized)
    campaign_items = []
    for campaign in campaigns:
        results = campaign.results or []
        results_not_displayed = 0
        for result in results:
            if result.user_id != userId:
                continue
            status_value = getattr(result.status, "value", result.status)
            if status_value != visualized_value:
                results_not_displayed += 1

        campaign_items.append(
            {
                "id": campaign.id,
                "title": campaign.title,
                "description": campaign.description,
                "resultsNotDisplayed": results_not_displayed,
            }
        )

    return {"campaigns": campaign_items}

@router.get("/getAllCampaigns", response_model=CampaignResponse)
def get_all_campaigns(db: Session = Depends(get_db)):
    campaigns = CampaignService.get_all_campaigns(db)
    campaigns_list = [_map_campaign(c) for c in campaigns]
    return {"campaigns": campaigns_list}


# ------------------------- PUT -------------------------------

@router.put("/updateCampaign/{campaign_id}", response_model=Campaign)
def update_campaign(campaign_id: int, campaign_update: CampaignUpdate, db: Session = Depends(get_db)):
    campaign = CampaignService.update_campaign(db, campaign_id, campaign_update)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return _map_campaign(campaign)


# ------------------------- DELETE -------------------------------

@router.delete("/deleteCampaign/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    deleted = CampaignService.delete_campaign(db, campaign_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return {"message": "Campaign deleted successfully"}