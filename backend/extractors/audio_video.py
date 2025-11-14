from pymediainfo import MediaInfo
from .utils import file_hashes

def extract_media_metadata(path):
    output = {}
    hashes = file_hashes(path)

    try:
        media = MediaInfo.parse(path)
        output["tracks"] = [track.to_data() for track in media.tracks]

        # Guess origin
        if any("iPhone" in str(t.to_data()) for t in media.tracks):
            output["origin_guess"] = "Likely recorded on an iPhone"
        elif any("Android" in str(t.to_data()) for t in media.tracks):
            output["origin_guess"] = "Android device recording"
        else:
            output["origin_guess"] = "Unknown"

        output["hashes"] = hashes
        return output

    except Exception as e:
        return {"error": str(e), "hashes": hashes}
