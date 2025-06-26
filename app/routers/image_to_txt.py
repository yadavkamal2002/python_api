from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract
import uuid, os, shutil
from app.utils import token_verify  # adjust this import as per your folder

router = APIRouter()

# Directories
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Token verification wrapper
def token_required(token: str = Depends(token_verify.token_required)):
    if not token:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

@router.post("/image-to-text/")
async def image_to_text(
        image: UploadFile = File(...),
        token_verified: str = Depends(token_required)
):
    # Generate unique filename
    image_filename = f"{uuid.uuid4().hex}.jpg"
    image_path = os.path.join(UPLOAD_DIR, image_filename)

    # Save uploaded file
    with open(image_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    try:
        # Load image and extract text
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)

        # Optionally delete after processing
        os.remove(image_path)

        return {
            "message": "Text extracted successfully",
           # JSONResponse(content={"text": extracted_text}),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")
