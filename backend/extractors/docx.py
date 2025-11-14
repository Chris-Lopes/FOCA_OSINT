from docx import Document
from .utils import file_hashes
import zipfile
import xml.etree.ElementTree as ET

def extract_docx_metadata(path):
    output = {}
    hashes = file_hashes(path)

    try:
        doc = Document(path)
        props = doc.core_properties

        output["properties"] = {
            "author": props.author,
            "title": props.title,
            "created": str(props.created),
            "modified": str(props.modified),
            "last_modified_by": props.last_modified_by,
            "revision": props.revision,
        }

        # Extract hidden metadata: XML relationships
        with zipfile.ZipFile(path, "r") as z:
            if "docProps/custom.xml" in z.namelist():
                xml = z.read("docProps/custom.xml")
                tree = ET.fromstring(xml)
                custom = {}
                for el in tree:
                    custom[el.tag] = el.text
                output["custom_properties"] = custom

        # OSINT guess
        if props.author:
            output["origin_guess"] = "User-generated document"
        else:
            output["origin_guess"] = "Downloaded / metadata stripped"

        output["hashes"] = hashes

        return output

    except Exception as e:
        return {"error": str(e), "hashes": hashes}
