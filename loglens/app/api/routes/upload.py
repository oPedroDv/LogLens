from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings, Settings
from app.core.database import get_db
from app.storage.queries import save_log_file, get_log_file_by_hash
from app.utils.hashing import compute_sha256
from app.schemas.response import LogFileResponse

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("", response_model=LogFileResponse, status_code=201)
async def upload_log_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LogFileResponse:
    
    from pathlib import Path
    extension = Path(file.filename or "").suffix.lower()

    if extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Extensão '{extension}' não suportada."
                f"Use uma das: {', '.join(settings.allowed_extensions)}"
            ),
        )
    
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")
    
    content_hash = compute_sha256(content)
    existing = get_log_file_by_hash(db, content_hash)
    if existing:
        response = LogFileResponse.model_validate(existing)
        response.is_duplicate = True
        return response
    
    stored_filename = f"{content_hash}{extension}"
    stored_path = settings.upload_dir / stored_filename
    stored_path.write_bytes(content)

    log_file = save_log_file(
        db=db,
        original_name = file.filename or "unknown",
        stored_path=str(stored_path),
        size_bytes=len(content),
        content_hash=content_hash,
        )
    
    return LogFileResponse.model_validate(log_file)
