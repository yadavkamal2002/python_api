from fastapi import APIRouter, UploadFile, File          #APIRouter = API define
from app.utils import token_verify
from fastapi import Depends
import os, uuid, shutil     # file save ,file name provide karna
import ffmpeg               # image ko compress ke liy

router = APIRouter()

# Token verification function (assuming it's implemented in utils.token_verify)
def token_required(token: str = Depends(token_verify.token_required)):
    """Ensure the user has a valid token."""
    if not token:  # Token validation
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

UPLOAD_DIR = "uploads"
COMPRESS_DIR = "compressed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(COMPRESS_DIR, exist_ok=True)

@router.post("/compress/")          # एक POST API है
async def compress_image(
        file: UploadFile = File(...), # image legi or compress karegi
    token_verified: str = Depends(token_required)
):
    input_ext = file.filename.split('.')[-1]            #  file extension निकाला (जैसे jpg, png)
    input_filename = f"{uuid.uuid4()}.{input_ext}"           # uniqe name file save uploads folder
    input_path = os.path.join(UPLOAD_DIR, input_filename)

    with open(input_path, "wb") as buffer:        # file local disk write
        shutil.copyfileobj(file.file, buffer)

    compressed_filename = f"compressed_{uuid.uuid4().hex}.jpg"          # compress file new name path
    compressed_path = os.path.join(COMPRESS_DIR, compressed_filename)

    try:
        (
            ffmpeg
            .input(input_path)
            .filter("scale", "iw*0.7", "ih*0.7")         # file resize karna
            .output(compressed_path, vframes=1, q=5, pix_fmt='yuvj420p')    #  q=  quality  q=1 high ,q=31 low quality
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )

        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(compressed_path)       #  compress image save space   show percentage
        reduction_percent = round(100 - (compressed_size / original_size * 100), 2)

        return {
            "message": "Image compressed successfully ✅",
            "original_file": input_filename,
            "compressed_file": compressed_filename,
            "original_size_kb": round(original_size / 1024, 2),
            "compressed_size_kb": round(compressed_size / 1024, 2),
            "reduction_percent": f"{reduction_percent}%"
        }

    except ffmpeg.Error as e:
        return {
            "error": "Compression failed ❌",  # compression में error, तो detailed error
            "details": e.stderr.decode("utf-8")
        }
