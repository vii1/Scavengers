# Conversión de datos entre DIV <-> PIL
from PIL import Image
from PIL.ImageFile import ImageFile
from PIL.ImagePalette import ImagePalette
from divfiles import pal, map as _map, fpg
from codecs import encode

def _get_colors(obj):
    """Obtiene los 256 pal_colors a partir una paleta de Image o ImagePalette"""
    assert isinstance(obj, ImageFile) or isinstance(obj, ImagePalette)
    if isinstance(obj, ImageFile):
        obj = obj.palette
    b = obj.getdata()[1]
    b = b''.join([b[a:a+3] for a in range(0, len(b), len(b)//256)])
    return pal.pal_rgb[256].parse(b)

def div_pal(obj):
    """Obtiene un PAL a partir de Image o ImagePalette"""
    return pal.pal_file(dict(colors=_get_colors(obj)))

def div_map(img:Image, code=1, description=None, cpoints=[]):
    """Obtiene un MAP a partir de Image"""
    if description == None:
        description = img.filename
    return _map.map_file.build(dict(
        header = dict(
            width = img.width,
            height = img.height,
            code = code,
            description = encode(description, 'CP850', 'replace')
        ),
        palette = dict(
            colors = _get_colors(img)
        ),
        cpoints = cpoints,
        pixels = img.getdata()
    ))