from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw, ImageFont
import uuid, os, shutil
from app.utils import token_verify

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "text_added"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def token_required(token: str = Depends(token_verify.token_required)):
    if not token:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

@router.post("/add-text/")
async def add_text_on_image(
        image: UploadFile = File(...),
        text: str = Form(...),
        x: int = Form(30),
        y: int = Form(30),
        font_size: int = Form(40),
        color: str = Form("white"),
        token_verified: str = Depends(token_required)
):
    ext = image.filename.split('.')[-1].lower()
    input_filename = f"{uuid.uuid4().hex}.{ext}"
    input_path = os.path.join(UPLOAD_DIR, input_filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    try:
        img = Image.open(input_path).convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Try to load a better font, fallback to default if not found
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        position = (x, y)
        draw.text(position, text, font=font, fill=color)

        if ext in ["jpg", "jpeg"]:
            img = img.convert("RGB")

        output_filename = f"text_{input_filename}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        img.save(output_path)

        media_type = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"

        return FileResponse(
            path=output_path,
            media_type=media_type,
            filename=output_filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add text: {str(e)}")
