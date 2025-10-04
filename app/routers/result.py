from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.result import ResultCreate, Result, ResultFeedback, ResultStatusUpdate
from app.services.result_service import (
    ResultService,
    CampaignNotFoundError,
    UserNotFoundError,
)
from app.database import get_db

router = APIRouter(prefix="/results", tags=["results"])


def _map_result(model) -> Result:
    feedback = ResultFeedback(
        like=model.feedback_like,
        comment=model.feedback_comment,
    )
    return Result(
        id=model.id,
        campaignId=model.campaign_id,
        originalImage=model.original_image,
        resultImage=model.result_image,
        type=model.type,
        status=model.status,
        created_at=model.created_at,
        feedback=feedback,
        userId=model.user_id,
    )


@router.post("/createResult", response_model=Result, status_code=status.HTTP_201_CREATED)
def create_result(payload: ResultCreate, db: Session = Depends(get_db)):
    try:
        result_model = ResultService.create_result(db, payload)
    except CampaignNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha nao encontrada"
        ) from None
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado"
        ) from None

    return _map_result(result_model)


@router.get("/getResult/{result_id}", response_model=Result)
def get_result_by_id(result_id: int, db: Session = Depends(get_db)):
    result = ResultService.get_result_by_id(db, result_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado nao encontrado"
        )

    return _map_result(result)


@router.get("/getResultByUser/{user_id}", response_model=List[Result])
def get_results_by_user(user_id: int, db: Session = Depends(get_db)):
    results = ResultService.get_results_by_user(db, user_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado nao encontrado para este usuario"
        )

    return [_map_result(result) for result in results]


@router.put("/updateResultStatus", response_model=Result)
def update_result_status(payload: ResultStatusUpdate, db: Session = Depends(get_db)):
    result, error = ResultService.update_result_status(db, payload.id, payload.status)
    if error == "RESULT_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado nao encontrado"
        )
    if error == "INVALID_STATUS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status invalido"
        )

    return _map_result(result)


