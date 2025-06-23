from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse  # FileResponse = MP3 file  भेजी जा सके
from fastapi import Depends
from app.utils import token_verify
import os, uuid
import ffmpeg

router = APIRouter()

# Token verification function (assuming it's implemented in utils.token_verify)
def token_required(
        token: str = Depends(token_verify.token_required)):
    """Ensure the user has a valid token."""
    if not token:  # Token validation
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "converted"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.post("/convert/")
async def convert_video_to_mp3(
        file: UploadFile = File(...),
        token_verified: str = Depends(token_required)
):
    input_filename = f"{uuid.uuid4()}_{file.filename}"
    input_path = os.path.join(UPLOAD_DIR, input_filename)


    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())

    output_filename = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format='mp3', acodec='libmp3lame', audio_bitrate='192k')
            .run(overwrite_output=True, quiet=True)
        )
    except ffmpeg.Error as e:
        return {"error": str(e)}

    return FileResponse(output_path, media_type="audio/mpeg", filename=output_filename) # MP3 को browser में download
