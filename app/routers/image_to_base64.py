from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.utils import token_verify
import base64
from PIL import Image
import io
import uuid
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "upload"
BASE64_OUTPUT_DIR = "base64_outputs"

# Ensure folders exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(BASE64_OUTPUT_DIR, exist_ok=True)

def token_required(token: str = Depends(token_verify.token_required)):
    if not token:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

@router.post("/image-to-base64/")
async def image_to_base64(
        file: UploadFile = File(...),
        token_verified: str = Depends(token_required)
):
    try:
        # ✅ Step 1: Save uploaded file in 'upload/' folder
        original_ext = file.filename.split('.')[-1]
        saved_filename = f"{uuid.uuid4().hex}.{original_ext}"
        upload_path = os.path.join(UPLOAD_DIR, saved_filename)

        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ✅ Step 2: Open image from saved path
        image = Image.open(upload_path)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # ✅ Step 3: Convert to base64
        base64_str = base64.b64encode(buffer.read()).decode('utf-8')

        # ✅ Step 4: Save base64 string as .txt file in 'base64_outputs/'
        output_filename = f"{uuid.uuid4().hex}.txt"
        output_path = os.path.join(BASE64_OUTPUT_DIR, output_filename)

        with open(output_path, "w") as f:
            f.write(base64_str)

        return {
            "original_file_saved": upload_path,
            "base64_file_saved": output_path,
            "message": "Image converted to base64 and saved successfully ✅"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
