import os
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException
from backend.app.services.crop_id_service import CropIdService

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/identify")
async def identify_crop_from_image(image: UploadFile = File(...)):
    """Upload a foliage photo to identify botanical crop species and family using MobileNetV3-Small."""
    allowed_exts = {".jpg", ".jpeg", ".png", ".webp"}
    ext = os.path.splitext(image.filename or "")[1].lower()
    if not ext:
        ext = ".jpg"
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'. Allowed: {allowed_exts}")

    filename = f"crop_id_{uuid.uuid4().hex[:8]}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, filename)

    content = await image.read()
    with open(saved_path, "wb") as f:
        f.write(content)

    result = CropIdService.identify_crop(saved_path)
    result["image_url"] = f"/uploads/{filename}"
    return result
