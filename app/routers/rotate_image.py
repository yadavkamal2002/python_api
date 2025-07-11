from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.utils import token_verify
from PIL import Image
import os, uuid, shutil

router = APIRouter()

# Token verification
def token_required(token: str = Depends(token_verify.token_required)):
    if not token:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

# Directories
UPLOAD_DIR = "uploads"
ROTATED_DIR = "rotated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ROTATED_DIR, exist_ok=True)

@router.post("/rotate-image/")
async def rotate_image(
        file: UploadFile = File(...),
        angle: int = Form(...),  # ⬅️ Rotation angle (90, 180, etc.)
        token_verified: str = Depends(token_required)
):
    if angle not in [90, 180, 270, 360]:
        raise HTTPException(status_code=400, detail="Angle must be 90, 180, 270 or 360 degrees.")

    input_ext = file.filename.split('.')[-1]
    input_filename = f"{uuid.uuid4()}.{input_ext}"
    input_path = os.path.join(UPLOAD_DIR, input_filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        img = Image.open(input_path).convert("RGB")
        rotated_img = img.rotate(-angle, expand=True)  # Negative to rotate clockwise

        rotated_filename = f"rotated_{uuid.uuid4().hex}.{input_ext}"
        rotated_path = os.path.join(ROTATED_DIR, rotated_filename)

        rotated_img.save(rotated_path)

        return {
            "message": f"Image rotated by {angle} degrees successfully ✅",
            "original_file": input_filename,
            "rotated_file": rotated_filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rotation failed: {str(e)}")
