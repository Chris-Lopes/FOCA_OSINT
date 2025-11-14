from PyPDF2 import PdfReader
from .utils import file_hashes

def extract_pdf_metadata(path):
    output = {}
    hashes = file_hashes(path)

    try:
        reader = PdfReader(path)

        info = reader.metadata or {}
        output["raw_metadata"] = {k[1:]: str(v) for k, v in info.items()}

        output["encrypted"] = reader.is_encrypted
        output["pages"] = len(reader.pages)

        # Extract fonts (OSINT) — indicates source program
        fonts = set()
        for page in reader.pages:
            if "/Font" in page.get_object():
                fonts.update(list(page["/Font"].keys()))
        output["fonts"] = list(fonts)

        # Possible origin guess
        if "Producer" in output["raw_metadata"]:
            prod = output["raw_metadata"]["Producer"].lower()
            if "microsoft" in prod:
                output["origin_guess"] = "Likely from MS Word / Office"
            elif "adobe" in prod:
                output["origin_guess"] = "Likely from Adobe PDF / Scanner"
            else:
                output["origin_guess"] = "Unknown producer"
        else:
            output["origin_guess"] = "No metadata available"

        output["hashes"] = hashes
        return output

    except Exception as e:
        return {"error": str(e), "hashes": hashes}
