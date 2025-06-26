from pydantic import BaseModel
from typing import Optional


# ✅ 1. Image Compression Response
class ImageCompressionResponse(BaseModel):
    message: str
    original_file: str
    compressed_file: str
    original_size_kb: float
    compressed_size_kb: float
    reduction_percent: str
    used_quality_q: int
    scale_used: str
    target_requested_kb: Optional[int]


# ✅ 2. Image Conversion Response
class ImageConversionResponse(BaseModel):
    message: str
    original_file: str
    converted_file: str


# ✅ 3. Image to Text (OCR) Response
class OCRResponse(BaseModel):
    message: str
    file_name: str
    file_size_kb: float
    text_length: int
    extracted_text: str


# ✅ 4. MP3 to Video / Video to MP3 Response (same structure: FileResponse)
# No Pydantic model needed because you return FileResponse
# But optionally, for metadata, you can do this:

class FileConversionMeta(BaseModel):
    message: str
    input_file: str
    output_file: str


# ✅ 5. General Error Response (optional)
class ErrorResponse(BaseModel):
    error: str
    details: Optional[str]
