from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

from extractors.pdf import extract_pdf_metadata
from extractors.docx import extract_docx_metadata
from extractors.pptx import extract_pptx_metadata
from extractors.image import extract_image_metadata
from extractors.audio_video import extract_media_metadata

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract")
async def extract_metadata(file: UploadFile):
    ext = file.filename.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    data = {"file": file.filename, "type": ext}

    if ext == "pdf":
        data["metadata"] = extract_pdf_metadata(tmp_path)
    elif ext == "docx":
        data["metadata"] = extract_docx_metadata(tmp_path)
    elif ext == "pptx":
        data["metadata"] = extract_pptx_metadata(tmp_path)
    elif ext in ["jpg", "jpeg", "png"]:
        data["metadata"] = extract_image_metadata(tmp_path)
    elif ext in ["mp3", "wav", "mp4", "mkv", "mov"]:
        data["metadata"] = extract_media_metadata(tmp_path)
    else:
        data["metadata"] = {"error": "Unsupported file type"}

    os.remove(tmp_path)
    return data
