from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from fastapi import Depends
from app.utils import token_verify
import os
import uuid
import ffmpeg

router = APIRouter()

# Token verification function (assuming it's implemented in utils.token_verify)
def token_required(token: str = Depends(token_verify.token_required)):
    """Ensure the user has a valid token."""
    if not token:  # Token validation
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

# Directories
UPLOAD_DIR = "uploads"
CREATED_DIR = "created"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CREATED_DIR, exist_ok=True)

@router.post("/convert/")
async def convert_to_video(
        audio: UploadFile = File(...), image: UploadFile = File(...),
        token_verified: str = Depends(token_required)
):
    # File paths
    audio_filename = f"{uuid.uuid4().hex}.mp3"
    image_filename = f"{uuid.uuid4().hex}.jpg"
    audio_path = os.path.join(UPLOAD_DIR, audio_filename)
    image_path = os.path.join(UPLOAD_DIR, image_filename)

    output_filename = f"{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(CREATED_DIR, output_filename)

    # Save uploaded files
    with open(audio_path, "wb") as a:
        a.write(await audio.read())
    with open(image_path, "wb") as i:
        i.write(await image.read())

    try:
        # Input streams
        video_input = ffmpeg.input(image_path, loop=1)
        audio_input = ffmpeg.input(audio_path)

        # Apply scaling to ensure even height
        video_stream = video_input.filter('scale', 'iw', 'if(mod(ih,2),ih-1,ih)')

        # Output combined stream
        (
            ffmpeg
            .output(
                video_stream,
                audio_input,
                output_path,
                vcodec='libx264',
                acodec='aac',
                audio_bitrate='192k',
                pix_fmt='yuv420p',
                shortest=None,
                **{'tune': 'stillimage'}
            )
            .run(overwrite_output=True, quiet=True)
        )

        return FileResponse(output_path, media_type="video/mp4", filename="converted.mp4")

    except ffmpeg.Error as e:
        return {
            "error": "Video conversion failed",
            "details": e.stderr.decode() if e.stderr else "Unknown error"
        }
