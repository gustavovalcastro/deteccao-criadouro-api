from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.result import Result, ResultFeedback, ResultStatusUpdate, ResultFeedbackUpdate, ResultImageUpdate, ImageUploadResponse, ResultType, Coordinates
from app.services.result_service import (
    ResultService,
    CampaignNotFoundError,
    UserNotFoundError,
)
from app.services.gcp_storage_service import GCPStorageService
from app.database import get_db
import os
import json

router = APIRouter(prefix="/results", tags=["results"])


def _map_result(model) -> Result:
    feedback = ResultFeedback(
        like=model.feedback_like,
        comment=model.feedback_comment,
    )
    coordinates = Coordinates(
        lat=model.lat,
        lng=model.lng,
    )
    return Result(
        id=model.id,
        campaignId=model.campaign_id,
        originalImage=model.original_image,
        resultImage=model.result_image,
        type=model.type,
        status=model.status,
        created_at=model.created_at,
        processed_at=model.processed_at,
        object_count=model.object_count,
        feedback=feedback,
        coordinates=coordinates,
        userId=model.user_id,
    )


@router.get("/getAllResults", response_model=List[Result])
def get_all_results(db: Session = Depends(get_db)):
    results = ResultService.get_all_results(db)
    return [_map_result(result) for result in results]


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


@router.put("/updateResultImage", response_model=Result)
def update_result_image(payload: ResultImageUpdate, db: Session = Depends(get_db)):
    result, error = ResultService.update_result_image_and_status(
        db, payload.id, payload.resultImage, payload.status, payload.object_count
    )
    if error == "RESULT_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado nao encontrado"
        )
    if error == "INVALID_STATUS" or error == "INVALID_STATUS_FOR_IMAGE_UPDATE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status invalido. Apenas 'finished' ou 'failed' sao permitidos para atualizacao de imagem"
        )
    if error == "OBJECT_COUNT_REQUIRED_FOR_FINISHED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="object_count e obrigatorio quando o status e 'finished'"
        )

    return _map_result(result)


@router.put("/updateResultFeedback", response_model=Result)
def update_result_feedback(payload: ResultFeedbackUpdate, db: Session = Depends(get_db)):
    result, error = ResultService.update_result_feedback(
        db, payload.id, payload.like, payload.comment
    )
    if error == "RESULT_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado nao encontrado"
        )

    return _map_result(result)


@router.delete("/deleteResult/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_result(result_id: int, db: Session = Depends(get_db)):
    success, error = ResultService.delete_result(db, result_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado nao encontrado"
        )
    
    return None


@router.post("/uploadImage", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_images(
    file: UploadFile = File(...),
    userId: int = Form(...),
    campaignId: Optional[Union[int, str]] = Form(None),
    type: ResultType = Form(...),
    coordinates: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):

    from app.models.enums.result import ResultType as ModelResultType
    
    gcp_storage = GCPStorageService()
    
    try:
        # Read file content
        contents = await file.read()
        
        # Get file extension
        file_extension = os.path.splitext(file.filename)[1].lstrip('.').lower()
        if not file_extension:
            file_extension = "jpg"  # Default extension
        
        # Upload to GCP Storage
        image_url = gcp_storage.upload_image(contents, file_extension)
        
        # Convert schema ResultType to model ResultType
        result_type = ModelResultType[type.value]
        
        # Handle campaignId: accept both int and str, convert empty string or "null" to None
        campaign_id_int = None
        if campaignId is not None:
            if isinstance(campaignId, int):
                campaign_id_int = campaignId
            elif isinstance(campaignId, str):
                campaign_id_str = campaignId.strip()
                if campaign_id_str and campaign_id_str.lower() != "null":
                    try:
                        campaign_id_int = int(campaign_id_str)
                    except (ValueError, TypeError):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="campaignId must be a valid integer or null"
                        )
            else:
                # Try to convert other types to int
                try:
                    campaign_id_int = int(campaignId)
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="campaignId must be a valid integer or null"
                    )
        
        # Parse coordinates JSON if provided
        lat = None
        lng = None
        if coordinates:
            # Handle string "null" explicitly
            if coordinates.strip().lower() == "null":
                lat = None
                lng = None
            else:
                try:
                    coords_data = json.loads(coordinates)
                    if coords_data is not None:
                        # Strict validation: lat and lng must be strings
                        lat = coords_data.get("lat")
                        lng = coords_data.get("lng") or coords_data.get("long")  # Support both "lng" and "long"
                        
                        # Validate types - must be strings or None
                        if lat is not None and not isinstance(lat, str):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid coordinates: 'lat' must be a string"
                            )
                        if lng is not None and not isinstance(lng, str):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid coordinates: 'lng' must be a string"
                            )
                        
                        # Validate that coordinate strings are numeric (optional but recommended)
                        if lat is not None:
                            try:
                                float(lat)
                            except (ValueError, TypeError):
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Invalid coordinates: 'lat' must be a numeric string"
                                )
                        if lng is not None:
                            try:
                                float(lng)
                            except (ValueError, TypeError):
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Invalid coordinates: 'lng' must be a numeric string"
                                )
                except HTTPException:
                    raise
                except (json.JSONDecodeError, TypeError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid coordinates format. Expected JSON object like {\"lat\": \"string\", \"lng\": \"string\"} or null"
                    )
        
        # Create result record
        result = ResultService.create_result_from_upload(
            db=db,
            image_url=image_url,
            user_id=userId,
            campaign_id=campaign_id_int,
            result_type=result_type,
            lat=lat,
            lng=lng,
        )
        
        return ImageUploadResponse(
            success=True,
            message="Imagem enviada com sucesso",
            uploaded_image=image_url,
            result_id=result.id,
            failed_count=0,
        )
        
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado"
        )
    except CampaignNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha nao encontrada"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload da imagem: {str(e)}"
        )


