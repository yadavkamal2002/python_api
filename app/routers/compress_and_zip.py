from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from app.utils import token_verify
import os, uuid, shutil, zipfile, ffmpeg

router = APIRouter()

UPLOAD_DIR = "uploads"
COMPRESS_DIR = "compressed"
ZIP_DIR = "zips"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(COMPRESS_DIR, exist_ok=True)
os.makedirs(ZIP_DIR, exist_ok=True)

def token_required(token: str = Depends(token_verify.token_required)):
    if not token:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

@router.post("/compress-multiple/")
async def compress_and_zip_images(
        files: list[UploadFile] = File(...),
        token_verified: str = Depends(token_required)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    compressed_files = []

    # STEP 1: Save & compress each file
    for file in files:
        ext = file.filename.split('.')[-1]
        input_filename = f"{uuid.uuid4()}.{ext}"
        input_path = os.path.join(UPLOAD_DIR, input_filename)

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        compressed_filename = f"compressed_{uuid.uuid4().hex}.jpg"
        compressed_path = os.path.join(COMPRESS_DIR, compressed_filename)

        try:
            (
                ffmpeg
                .input(input_path)
                .filter("scale", "iw*0.7", "ih*0.7")
                .output(compressed_path, vframes=1, q=5, pix_fmt='yuvj420p')
                .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
            )
            compressed_files.append(compressed_path)

        except ffmpeg.Error as e:
            print(f"Compression failed for {file.filename}: {e.stderr.decode('utf-8')}")

    if not compressed_files:
        raise HTTPException(status_code=500, detail="Compression failed for all files.")

    # STEP 2: Create ZIP file
    zip_filename = f"compressed_{uuid.uuid4().hex}.zip"
    zip_path = os.path.join(ZIP_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in compressed_files:
            zipf.write(file_path, arcname=os.path.basename(file_path))

    # STEP 3: Return ZIP file
    return FileResponse(zip_path, filename=zip_filename, media_type="application/zip")
