from pptx import Presentation
from .utils import file_hashes

def extract_pptx_metadata(path):
    output = {}
    hashes = file_hashes(path)

    try:
        prs = Presentation(path)
        prop = prs.core_properties

        output["properties"] = {
            "author": prop.author,
            "title": prop.title,
            "created": str(prop.created),
            "modified": str(prop.modified),
            "last_modified_by": prop.last_modified_by,
            "revision": prop.revision,
        }

        # Count slides
        output["slide_count"] = len(prs.slides)

        output["hashes"] = hashes
        return output

    except Exception as e:
        return {"error": str(e), "hashes": hashes}
