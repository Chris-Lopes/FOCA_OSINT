import zipfile
from .utils import file_hashes

def extract_zip_metadata(path):
    hashes = file_hashes(path)

    try:
        z = zipfile.ZipFile(path)
        file_list = []
        for f in z.infolist():
            file_list.append({
                "filename": f.filename,
                "size": f.file_size,
                "compressed": f.compress_size,
                "date": f.date_time
            })

        return {
            "entries": file_list,
            "hashes": hashes,
            "origin_guess": "Archive file — may contain embedded metadata"
        }

    except Exception as e:
        return {"error": str(e), "hashes": hashes}
