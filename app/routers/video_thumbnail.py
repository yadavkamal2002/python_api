from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from app.utils import token_verify
import os, uuid, shutil
import ffmpeg

router = APIRouter()

# Token verify
def token_required(token: str = Depends(token_verify.token_required)):
    if not token:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

# Paths
UPLOAD_DIR = "uploads"
THUMBNAIL_DIR = "thumbnails"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

@router.post("/thumbnail/")
async def generate_video_thumbnail(
        file: UploadFile = File(...),
        time_in_seconds: int = Form(1),
        token_verified: str = Depends(token_required)
):
    # Save uploaded video
    ext = file.filename.split('.')[-1]
    input_filename = f"{uuid.uuid4()}.{ext}"
    input_path = os.path.join(UPLOAD_DIR, input_filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Output path
    thumbnail_filename = f"thumb_{uuid.uuid4().hex}.jpg"
    thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail_filename)

    try:
        # Run ffmpeg command
        (
            ffmpeg
            .input(input_path, ss=time_in_seconds)
            .output(thumbnail_path, vframes=1)
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )

        # ✅ Check if thumbnail was actually created
        if not os.path.exists(thumbnail_path):
            raise HTTPException(status_code=500, detail="Thumbnail not created. Check video or time position.")

        return FileResponse(
            path=thumbnail_path,
            media_type="image/jpeg",
            filename=thumbnail_filename
        )

    except ffmpeg.Error as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg error: {e.stderr.decode()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
