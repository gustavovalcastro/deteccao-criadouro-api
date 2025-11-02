from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CampaignResultFeedback(BaseModel):
    like: Optional[bool] = None
    comment: Optional[str] = None


class CampaignResult(BaseModel):
    id: int
    originalImage: str
    resultImage: Optional[str] = None
    type: str
    status: str
    feedback: CampaignResultFeedback


class CampaignCreate(BaseModel):
    title: str
    description: str
    city: str
    campaignInfos: Optional[List[str]] = Field(default=None, alias="campaign_infos")
    instructionInfos: Optional[List[str]] = Field(default=None, alias="instruction_infos")
    created_at: Optional[datetime] = None
    finish_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    campaignInfos: Optional[List[str]] = Field(default=None, alias="campaign_infos")
    instructionInfos: Optional[List[str]] = Field(default=None, alias="instruction_infos")
    created_at: Optional[datetime] = None
    finish_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class CampaignBasicResponse(BaseModel):
    id: int
    title: str
    description: str
    city: str
    campaignInfos: Optional[List[str]] = Field(default=None, alias="campaign_infos")
    instructionInfos: Optional[List[str]] = Field(default=None, alias="instruction_infos")
    created_at: datetime
    finish_at: Optional[datetime]

    class Config:
        from_attributes = True
        populate_by_name = True


class Campaign(BaseModel):
    id: int
    title: str
    description: str
    city: str
    campaignInfos: Optional[List[str]] = Field(default=None, alias="campaign_infos")
    instructionInfos: Optional[List[str]] = Field(default=None, alias="instruction_infos")
    created_at: datetime
    finish_at: Optional[datetime]
    results: List[CampaignResult] = Field(default_factory=list)

    class Config:
        from_attributes = True
        populate_by_name = True


class CampaignResponse(BaseModel):
    campaigns: List[Campaign]


class UserCampaignItem(BaseModel):
    id: int
    title: str
    description: str
    resultsNotDisplayed: int


class UserCampaignsResponse(BaseModel):
    campaigns: List[UserCampaignItem]