from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

# Import extractors
from extractors.pdf import extract_pdf_metadata
from extractors.docx import extract_docx_metadata
from extractors.pptx import extract_pptx_metadata
from extractors.image import extract_image_metadata
from extractors.audio_video import extract_media_metadata


app = FastAPI()

# Allow frontend CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/extract")
async def extract_metadata(file: UploadFile):
    # Extract file extension
    ext = file.filename.split(".")[-1].lower()

    # Save uploaded file to a temporary path
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    data = {"file": file.filename, "type": ext}

    # ---------------------------
    # ROUTING BASED ON EXTENSION
    # ---------------------------

    # PDF
    if ext == "pdf":
        data["metadata"] = extract_pdf_metadata(tmp_path)

    # DOCX
    elif ext == "docx":
        data["metadata"] = extract_docx_metadata(tmp_path)

    # PPTX
    elif ext == "pptx":
        data["metadata"] = extract_pptx_metadata(tmp_path)

    # XLSX / Excel
    elif ext in ["xlsx", "xlsm"]:
        from extractors.xlsx import extract_xlsx_metadata
        data["metadata"] = extract_xlsx_metadata(tmp_path)

    # IMAGES (HEIC supported here)
    elif ext in ["jpg", "jpeg", "png", "webp", "bmp", "tiff", "heic", "heif"]:
        data["metadata"] = extract_image_metadata(tmp_path)

    # AUDIO / VIDEO
    elif ext in ["mp3", "wav", "aac", "mp4", "mkv", "mov"]:
        data["metadata"] = extract_media_metadata(tmp_path)

    # ARCHIVES
    elif ext in ["zip", "rar"]:
        from extractors.zipmeta import extract_zip_metadata
        data["metadata"] = extract_zip_metadata(tmp_path)

    # UNSUPPORTED FORMAT
    else:
        data["metadata"] = {"error": f"Unsupported file type: {ext}"}

    # Cleanup temporary file
    os.remove(tmp_path)

    return data
