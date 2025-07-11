# app/routers/image_to_thumbnail.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from app.utils import token_verify
from PIL import Image
import os, uuid, shutil, zipfile, io

router = APIRouter()

UPLOAD_DIR = "uploads"
THUMBNAIL_DIR = "thumbnails"
ZIP_DIR = "zips"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)
os.makedirs(ZIP_DIR, exist_ok=True)

def token_required(token: str = Depends(token_verify.token_required)):
    if not token:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

@router.post("/thumbnail-multiple/")
async def generate_thumbnails(
        files: list[UploadFile] = File(...),
        size: int = 128,
        token_verified: str = Depends(token_required)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    thumbnail_files = []

    for file in files:
        try:
            ext = file.filename.split('.')[-1]
            input_filename = f"{uuid.uuid4()}.{ext}"
            input_path = os.path.join(UPLOAD_DIR, input_filename)

            # Save uploaded image
            with open(input_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Open and create thumbnail
            image = Image.open(input_path)
            image.thumbnail((size, size))

            thumb_filename = f"thumbnail_{uuid.uuid4().hex}.png"
            thumb_path = os.path.join(THUMBNAIL_DIR, thumb_filename)

            image.save(thumb_path, "PNG")
            thumbnail_files.append(thumb_path)

        except Exception as e:
            print(f"Thumbnail generation failed for {file.filename}: {str(e)}")

    if not thumbnail_files:
        raise HTTPException(status_code=500, detail="Thumbnail generation failed for all files.")

    # Create ZIP
    zip_filename = f"thumbnails_{uuid.uuid4().hex}.zip"
    zip_path = os.path.join(ZIP_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in thumbnail_files:
            zipf.write(file_path, arcname=os.path.basename(file_path))

    return FileResponse(zip_path, filename=zip_filename, media_type="application/zip")
