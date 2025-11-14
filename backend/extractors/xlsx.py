import zipfile
from .utils import file_hashes
import xml.etree.ElementTree as ET

def extract_xlsx_metadata(path):
    output = {}
    hashes = file_hashes(path)

    try:
        with zipfile.ZipFile(path, "r") as z:
            # Core properties
            core_xml = z.read("docProps/core.xml")
            tree = ET.fromstring(core_xml)

            core_info = {}
            for el in tree:
                tag = el.tag.split("}")[1]
                core_info[tag] = el.text

            output["properties"] = core_info

        output["hashes"] = hashes
        return output

    except Exception as e:
        return {"error": str(e), "hashes": hashes}
