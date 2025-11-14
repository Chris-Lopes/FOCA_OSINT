import exifread
from PIL import Image, ImageChops, ImageEnhance
import pillow_heif  # HEIC/HEIF support
import hashlib
import subprocess
import os

# Enable HEIF/HEIC support inside PIL
pillow_heif.register_heif_opener()


def calculate_hashes(path):
    with open(path, "rb") as f:
        data = f.read()
    return {
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha512": hashlib.sha512(data).hexdigest(),
    }


def extract_png_text(path):
    try:
        output = subprocess.check_output(["identify", "-verbose", path]).decode()
        return [line.strip() for line in output.split("\n") if any(c in line for c in ["tEXt", "iTXt", "zTXt"])]
    except:
        return []


def extract_icc_profile(path):
    try:
        img = Image.open(path)
        return "Present" if img.info.get("icc_profile") else "None"
    except:
        return "Error reading ICC"


def gps_to_map(tags):
    try:
        lat = tags["GPS GPSLatitude"]
        lon = tags["GPS GPSLongitude"]
        lat_ref = tags["GPS GPSLatitudeRef"]
        lon_ref = tags["GPS GPSLongitudeRef"]

        def convert(values):
            d, m, s = [float(x.num) / float(x.den) for x in values]
            return d + m/60 + s/3600

        lat_dec = convert(lat.values)
        lon_dec = convert(lon.values)

        if lat_ref.values != "N":
            lat_dec = -lat_dec
        if lon_ref.values != "E":
            lon_dec = -lon_dec

        return f"https://www.google.com/maps?q={lat_dec},{lon_dec}"
    except:
        return None


def origin_guess(exif: dict):
    if "Image Model" in exif:
        model = exif["Image Model"].lower()
        if "iphone" in model:
            return "Captured using an iPhone"
        if "samsung" in model:
            return "Captured using a Samsung device"
        return "Captured using a camera"

    if len(exif) == 0:
        return "Likely screenshot or metadata-stripped social media upload"

    return "Unknown"


def ela_analysis(path):
    try:
        img = Image.open(path).convert("RGB")

        # Save a temporary JPEG
        temp_jpeg = path + "_temp.jpg"
        img.save(temp_jpeg, "JPEG", quality=90)

        resaved = Image.open(temp_jpeg)
        diff = ImageChops.difference(img, resaved)

        ela_img = ImageEnhance.Brightness(diff).enhance(30)

        out_path = path + "_ELA.png"
        ela_img.save(out_path)

        os.remove(temp_jpeg)

        return out_path
    except:
        return None


def extract_image_metadata(path):
    result = {}

    # Hashes
    result["hashes"] = calculate_hashes(path)

    # EXIF (works with HEIC now)
    try:
        with open(path, "rb") as f:
            tags = exifread.process_file(f)
        exif = {k: str(v) for k, v in tags.items()}
    except:
        exif = {}

    result["exif"] = exif

    # PNG tEXt metadata
    result["png_text"] = extract_png_text(path)

    # ICC Profile
    result["icc_profile"] = extract_icc_profile(path)

    # GPS Map
    result["gps_map"] = gps_to_map(tags if exif else {})

    # OSINT origin
    result["osint_guess"] = origin_guess(exif)

    # Reverse Image Search Links
    result["reverse_search"] = {
        "google": "https://lens.google.com/",
        "tineye": "https://tineye.com/",
        "yandex": "https://yandex.com/images/"
    }

    # ELA output
    result["ela_image"] = ela_analysis(path)

    return result
