from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from app.utils import token_verify
from PIL import Image, ImageDraw, ImageFont
import os, uuid

router = APIRouter()

UPLOAD_DIR = "uploads"
WATERMARK_DIR = "watermarked"

# if not os.path.exists(UPLOAD_DIR):
#     os.makedirs(UPLOAD_DIR)
#     print(f"📂 Created folder: {UPLOAD_DIR}")

if not os.path.exists(WATERMARK_DIR):
    os.makedirs(WATERMARK_DIR)
    print(f"📂 Created folder: {WATERMARK_DIR}")

def token_required(token: str = Depends(token_verify.token_required)):
    if not token:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token

@router.post("/add-watermark/")
async def add_watermark(
        image: UploadFile = File(...),
        watermark_text: str = Form(...),
        token_verified: str = Depends(token_required)
):
    try:
        ext = image.filename.split('.')[-1]
        input_filename = f"{uuid.uuid4().hex}.{ext}"
        input_path = os.path.join(UPLOAD_DIR, input_filename)

        with open(input_path, "wb") as f:
            f.write(await image.read())

        img = Image.open(input_path).convert("RGBA")
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))

        draw = ImageDraw.Draw(txt_layer)
        font_size = max(int(min(img.size) / 15), 30)

        # 🔥 Recommended font path
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            print("⚠️ Font not found, using default.")
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = img.width - text_width - 10
        y = img.height - text_height - 10

        # ✅ Full white, fully visible
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 255))

        watermarked_img = Image.alpha_composite(img, txt_layer)

        output_filename = f"watermarked_{uuid.uuid4().hex}.jpg"
        output_path = os.path.join(WATERMARK_DIR, output_filename)
        watermarked_img.convert("RGB").save(output_path, "JPEG")

        return FileResponse(output_path, filename=output_filename)

    except Exception as e:
        print("🔥 ERROR:", str(e))
        raise HTTPException(status_code=500, detail=f"Error adding watermark: {str(e)}")
