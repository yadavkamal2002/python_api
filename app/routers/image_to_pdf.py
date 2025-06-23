from fastapi import APIRouter, UploadFile, File          #APIRouter = API define
from app.utils import token_verify
from fastapi.responses import FileResponse
from PIL import Image
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
pdf_DIR = "pdf"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(pdf_DIR, exist_ok=True)

@router.post("/image-to-pdf/")
async def convert_image_to_pdf(
        file: UploadFile = File(...), # image legi or compress karegi
        token_verified: str = Depends(token_required)
):
    input_ext = file.filename.split('.')[-1]            #  file extension निकाला (जैसे jpg, png)
    input_filename = f"{uuid.uuid4()}.{input_ext}"           # uniqe name file save uploads folder
    input_path = os.path.join(UPLOAD_DIR, input_filename)

    with open(input_path, "wb") as buffer:        # file local disk write
        shutil.copyfileobj(file.file, buffer)

    image = Image.open(input_path).convert("RGB")
    pdf_filename = f"pdf_{uuid.uuid4().hex}.jpg"          # compress file new name path
    pdf_path = os.path.join(pdf_DIR, pdf_filename)
    image.save(pdf_path, "PDF")

    return {
        "message": "Image compressed successfully ✅",
        "original_file": input_filename,
        "pdf_file": pdf_filename
    }


