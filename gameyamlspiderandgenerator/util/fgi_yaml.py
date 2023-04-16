import zipfile
from io import BytesIO
from textwrap import dedent
from typing import AnyStr

from PIL import Image
from loguru import logger
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PreservedScalarString


def pss_dedent(x: AnyStr) -> PreservedScalarString:
    return PreservedScalarString(dedent(x))


fgi = YAML(typ=["rt", "string"])
fgi.indent(sequence=4, offset=2)
fgi.preserve_quotes = True
fgi.width = 4096


def dump_to_yaml(data: dict) -> AnyStr:
    temp = fgi.dump_to_string(data)
    for i in list(data.keys())[1:]:
        temp = temp.replace("\n" + i, "\n\n" + i)
    return temp


def process_thumbnail(img_byte: bytes):
    img = Image.open(BytesIO(img_byte))
    if img.size[0] % 360 == img.size[1] % 168 == 0:
        img_resize = img.resize((360, 168))
        ret_byte = BytesIO()
        img_resize.save(ret_byte, format="PNG", optimize=True, quality=85)
        return ret_byte.getvalue()
    logger.warning("Thumbnails cannot be scaled down.")
    return img_byte


class YamlData:
    raw_dict: dict

    def __init__(self, raw_data: dict):
        self.raw_dict = raw_data

    def __str__(self):
        return dump_to_yaml({**self.raw_dict["thumbnail"], "thumbnail": 'thumbnail.png'})

    def __bytes__(self):
        from ..util.spider import get_bytes
        _io = BytesIO()
        img = get_bytes(self.raw_dict["thumbnail"])
        zip_data = zipfile.ZipFile(_io, 'w', zipfile.ZIP_STORED)
        zip_data.writestr('thumbnail.png', process_thumbnail(img))

        zip_data.writestr(self.raw_dict['name'] + ".yaml",
                          dump_to_yaml({**self.raw_dict["thumbnail"], "thumbnail": 'thumbnail.png'}))
        zip_data.close()
        return _io.getvalue()
