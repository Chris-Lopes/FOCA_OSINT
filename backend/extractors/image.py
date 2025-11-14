import exifread
from PIL import Image, ImageChops, ImageEnhance
import hashlib
import subprocess
import json
import os

def calculate_hashes(path):
    hashes = {"md5": "", "sha1": "", "sha256": "", "sha512": ""}
    with open(path, "rb") as f:
        data = f.read()
        hashes["md5"] = hashlib.md5(data).hexdigest()
        hashes["sha1"] = hashlib.sha1(data).hexdigest()
        hashes["sha256"] = hashlib.sha256(data).hexdigest()
        hashes["sha512"] = hashlib.sha512(data).hexdigest()
    return hashes


def extract_png_text(path):
    try:
        output = subprocess.check_output(["identify", "-verbose", path]).decode()
        # Extract tEXt chunks
        chunks = []
        for line in output.split("\n"):
            if "tEXt" in line or "iTXt" in line or "zTXt" in line:
                chunks.append(line.strip())
        return chunks
    except:
        return []


def extract_icc_profile(path):
    try:
        img = Image.open(path)
        icc = img.info.get("icc_profile")
        return "Present" if icc else "None"
    except:
        return "Error loading ICC"


def guess_origin(metadata, hashes):
    # Basic heuristics
    if "Image Model" in metadata:
        return "Taken from a camera or mobile phone"
    if len(metadata) == 0:
        if hashes["md5"].startswith("00000"):
            return "Likely from a compressed web upload"
        return "Possibly a screenshot / social media download"
    if "GPS GPSLatitude" in metadata:
        return "Original image with GPS data (camera)"
    return "Unknown (no strong indicators)"


def gps_to_map(tags):
    try:
        lat = tags["GPS GPSLatitude"]
        lon = tags["GPS GPSLongitude"]
        lat_ref = tags["GPS GPSLatitudeRef"]
        lon_ref = tags["GPS GPSLongitudeRef"]

        def convert(value):
            d, m, s = [float(x.num) / float(x.den) for x in value.values]
            return d + (m / 60) + (s / 3600)

        lat_dec = convert(lat)
        lon_dec = convert(lon)

        if lat_ref.values != "N":
            lat_dec = -lat_dec
        if lon_ref.values != "E":
            lon_dec = -lon_dec

        google_maps = f"https://www.google.com/maps?q={lat_dec},{lon_dec}"
        return google_maps
    except:
        return None


def ela_analysis(path):
    try:
        original = Image.open(path)
        original = original.convert("RGB")

        # Save at a lower quality to detect differences
        temp = path + "_resaved.jpg"
        original.save(temp, "JPEG", quality=90)

        resaved = Image.open(temp)
        diff = ImageChops.difference(original, resaved)

        enhancer = ImageEnhance.Brightness(diff)
        ela_image = enhancer.enhance(30)

        ela_output = path + "_ela.png"
        ela_image.save(ela_output)

        os.remove(temp)

        return ela_output
    except:
        return None


def extract_image_metadata(path):
    output = {}

    # 1. EXIF METADATA
    try:
        tags = exifread.process_file(open(path, "rb"))
        output["exif"] = {k: str(v) for k, v in tags.items()}
    except:
        output["exif"] = {}

    # 2. HASHES
    output["hashes"] = calculate_hashes(path)

    # 3. PNG metadata (tEXt blocks)
    output["png_text"] = extract_png_text(path)

    # 4. ICC Color Profile
    output["icc_profile"] = extract_icc_profile(path)

    # 5. GPS → Google Maps
    gps_link = gps_to_map(tags if "exif" in output else {})
    output["gps_map"] = gps_link

    # 6. OSINT Origin Guess
    output["osint_guess"] = guess_origin(output["exif"], output["hashes"])

    # 7. Reverse Image Search Links
    filename = os.path.basename(path)
    output["reverse_search"] = {
        "google": f"https://www.google.com/searchbyimage?image_url=file://{filename}",
        "tineye": f"https://tineye.com/search?url=file://{filename}"
    }

    # 8. Error Level Analysis (ELA)
    ela_file = ela_analysis(path)
    output["ela_image"] = ela_file  # Can display in frontend

    return output
