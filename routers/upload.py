from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pathlib import Path
import os
import uuid

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Ensure upload directory exists
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file"""
    # Check if file was uploaded
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded"
        )
    
    # Check file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Return file path (relative to serve with static files)
    return {
        "message": "File uploaded successfully",
        "image": f"/{file_path.as_posix()}"
    }
