# Conversión de datos entre DIV <-> MagickWand
from wand.image import Image
from wand.color import Color
from divfiles import pal, map as _map, fpg


dither_method = 'floyd_steinberg'


def _get_impalette(img: Image):
    return [img.color_map(idx) for idx in range(img.colors)]


def _get_colors(impalette):
    """Obtiene los 256 pal_colors de una Image."""
    palette = sum([[c.red_int8 >> 2, c.green_int8 >> 2, c.blue_int8 >> 2]   # valores en rango (0..63)
                   for c in impalette if c.alpha_int8 >= 128],     # sólo colores opacos
                  start=[0, 0, 0])  # primer color = negro transparente
    if len(palette) < 256 * 3:
        palette += [0] * (256 * 3 - len(palette))
    return pal.pal_rgb[256].parse(bytes(palette))


def div_pal(img: Image):
    """Obtiene un PAL a partir de una Image ya reducida (255 colores o transparente + 255)."""
    return pal.pal_file(dict(colors=_get_colors(_get_impalette(img))))


def _make_pal_lookup(impalette):
    pal_lookup = {}
    idx = 1
    for c in impalette:
        if c.alpha_int8 >= 128:
            pal_lookup[bytes([c.red_int8, c.green_int8, c.blue_int8])] = idx
            idx += 1
    return pal_lookup

def _get_buffer_bytes(img: Image, impalette=None, pal_lookup=None):
    if not impalette:
        impalette = _get_impalette(img)
    if not pal_lookup:
        pal_lookup = _make_pal_lookup(impalette)
    buffer_rgba = img.export_pixels()
    buffer_bytes = bytes([
        pal_lookup[bytes(buffer_rgba[p:p + 3])]
        if buffer_rgba[p + 3] >= 128 else 0
        for p in range(0, len(buffer_rgba), 4)
    ])
    assert(len(buffer_bytes) == img.width * img.height)
    return buffer_bytes
    
def div_map(img: Image, code=1, description='', cpoints=[]):
    """Obtiene un MAP a partir de Image (ya reducida!)"""
    impalette = _get_impalette(img)
    return _map.map_file.build(dict(
        header=dict(
            width=img.width,
            height=img.height,
            code=code,
            description=bytes(description, 'CP850', 'replace')),
        palette=dict(colors=_get_colors(impalette)),
        cpoints=cpoints,
        pixels=_get_buffer_bytes(img, impalette)))

def div_reduce_image(img: Image, colors=256, dither=False, colorkey=None, fuzz=0):
    """Posteriza y cuantiza un Image para reducirlo a 256 colores y que sea compatible con DIV.

    :param img: La imagen
    :param colors: Número máximo de colores
    :param dither: Aplicar dithering
    :param colorkey: Sustituir este color por el negro transparente
    :type color: :class:`wand.color.Color`
    :param fuzz: Tolerancia para el colorkey
    """
    if colors > 256 or colors < 1:
        raise ValueError("colors debe estar entre 1..256")
    img.colorspace = 'rgb'
    if colorkey:
        img.transparent_color(colorkey, 0.0, fuzz)
    img.posterize(64, dither_method if dither else 'no')
    img.threshold(channel='alpha')
    if colors==256 and img.range_channel('alpha') == (img.quantum_range, img.quantum_range):
        # La imagen no tiene transparencia, por lo que tendremos que cuantizar a 255 colores
        img.quantize(255, 'rgb', 0, not dither, False) # dither está invertido en Wand+IM6 ¿?¿?¿?
        img.type='palette'
    else:
        img.quantize(colors, 'rgb', 0, not dither, False) # dither está invertido en Wand+IM6 ¿?¿?¿?
        img.type='palettealpha'
    return img

def div_reduce_images(imgs: list, colors=256, dither=False, colorkey=None, fuzz=0):
    """Posteriza y cuantiza varias Images conjuntamente para reducirlas a la misma paleta
    y que sean compatibles con DIV
    
    :param imgs: Lista de Image
    :param colors: Número máximo de colores
    :param dither: Aplicar dithering
    :param colorkey: Sustituir este color por el negro transparente
    :type color: :class:`wand.color.Color`
    :param fuzz: Tolerancia para el colorkey
    """
    if colors > 256 or colors < 1:
        raise ValueError("colors debe estar entre 1..256")
    margin = 5
    totalwidth = sum([i.width for i in imgs]) + margin * (len(imgs) + 1)
    totalheight = max([i.height for i in imgs]) + margin * 2
    with Image(width=totalwidth, height=totalheight, colorspace='rgb') as bigimg:
        x = margin
        for i in imgs:
            bigimg.composite(i, left=x, top=margin)
            x += i.width + margin
        div_reduce_image(bigimg, colors, dither, colorkey, fuzz)
        newimgs = []
        x = margin
        for i in imgs:
            img = bigimg[x:x + i.width, margin:margin + i.height]
            newimgs.append(img)
            x += i.width + margin
        return (newimgs, _get_impalette(bigimg))


def _cut_filename(filename:str):
    from os.path import basename
    f = basename(filename)
    if len(f)>12:
        name, ext = f.split('.', 1)
        f = name[:8] + '.' + ext[:3]
    return f


def div_fpg(imgs: list, impalette:list, descpattern=None):
    code = 1
    map_dicts = []
    pal_lookup = _make_pal_lookup(impalette)
    # Hay que unificar la paleta… otra vez…
    # totalwidth = sum([i.width for i in imgs])
    # totalheight = max([i.height for i in imgs])
    # with Image(width=totalwidth, height=totalheight, colorspace='rgb') as bigimg:
    #     x = 0
    #     for i in imgs:
    #         bigimg.composite(i, left=x, top=0)
    #     bigimg.unique_colors()
    #     bigimg.quantize(256,bigimg.colorspace,0,True,False)
    #     impalette = _get_impalette(bigimg)
    #     pal_lookup = _make_pal_lookup(impalette)
    #     #print(pal_lookup)
    for obj in imgs:
        if isinstance(obj, dict):
            img = obj['image']
            if 'code' in obj:
                code = obj['code']
            map_dicts.append({
                'code': code,
                'description': bytes(
                    obj['description'] if 'description' in obj else (descpattern % code if descpattern else ''),
                    'CP850', 'replace')[:32],
                'filename': bytes(_cut_filename(obj['filename'] if 'filename' in obj else ''),
                    'CP850', 'replace'),
                'width': img.width,
                'height': img.height,
                'cpoints': obj['cpoints'] if 'cpoints' in obj else [],
                'pixels': _get_buffer_bytes(img, impalette, pal_lookup)
            })
        else:
            img = obj
            map_dicts.append({
                'code': code,
                'description': bytes(
                    descpattern % code if descpattern else '',
                    'CP850', 'replace')[:32],
                'filename': b'',
                'width': img.width,
                'height': img.height,
                'cpoints': [],
                'pixels': _get_buffer_bytes(img, impalette, pal_lookup)
            })
        code += 1
    return fpg.fpg_file.build({
        'palette': { 'colors': _get_colors(impalette) },
        'maps': map_dicts
    })

