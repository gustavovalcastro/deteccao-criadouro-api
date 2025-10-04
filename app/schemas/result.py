import enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ResultType(str, enum.Enum):
    terreno = "terreno"
    propriedade = "propriedade"


class ResultStatus(str, enum.Enum):
    visualized = "visualized"
    finished = "finished"
    processing = "processing"
    failed = "failed"


class ResultFeedback(BaseModel):
    like: bool = False
    comment: Optional[str] = None


class ResultBase(BaseModel):
    originalImage: str
    resultImage: Optional[str] = None
    type: ResultType
    status: ResultStatus
    feedback: Optional[ResultFeedback] = None


class ResultCreate(ResultBase):
    campaignId: Optional[int] = None
    userId: Optional[int] = None


class Result(ResultBase):
    id: int
    campaignId: Optional[int] = None
    created_at: datetime
    feedback: ResultFeedback
    userId: Optional[int] = None

    class Config:
        from_attributes = True


class ResultStatusUpdate(BaseModel):
    id: int
    status: ResultStatus