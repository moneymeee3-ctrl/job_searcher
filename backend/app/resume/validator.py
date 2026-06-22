"""EMBEDHUNT AI — Resume Validator"""
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from app.common.constants import MAX_RESUME_SIZE_BYTES, ALLOWED_RESUME_EXTENSIONS, MIN_RESUME_TEXT_LENGTH

async def validate_resume_file(file: UploadFile) -> bytes:
    filename = file.filename or "resume.pdf"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Unsupported type '{ext}'. Allowed: PDF, DOCX, TXT")
    content = await file.read()
    if not content:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "File is empty")
    if len(content) > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, f"File too large. Max: {MAX_RESUME_SIZE_BYTES//1024//1024}MB")
    return content

def validate_parsed_text(text: str) -> None:
    if not text or len(text) < MIN_RESUME_TEXT_LENGTH:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Could not extract sufficient text. Please upload a text-based PDF.")
