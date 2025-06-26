from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from decouple import config

from app.routers import image, video_to_mp3, mp3_to_video, image_to_pdf, image_to_txt


app = FastAPI(
    title="Media Processing API",
    docs_url=None, redoc_url=None, openapi_url = None
)

#=========== for basic authentication before opening docs ================
security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = config("DOCS_USERNAME")
    correct_password = config("DOCS_PASSWORD")
    if not (credentials.username == correct_username and credentials.password == correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title="FastAPI", version="0.1.0", routes=app.routes)

#===========make custom exception structure ===============================
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.detail},
            headers={"WWW-Authenticate": "Basic"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "data": {},
            "message": exc.detail,
        },
    )


# Include routers
app.include_router(image.router, prefix="/image", tags=["Image Compression"])
app.include_router(video_to_mp3.router, prefix="/video", tags=["Video to MP3"])
app.include_router(mp3_to_video.router, prefix="/mp3", tags=["MP3 to Video"])
app.include_router(image_to_pdf.router, prefix="/pdf", tags=["Image to pdf"])
app.include_router(image_to_txt.router, prefix="/text", tags=["Image to text"])