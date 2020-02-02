from construct import *
from .pal import pal_rgb, pal_range

# Nota: las cadenas mejor (des)codificarlas aparte ya que Construct no trae
# soporte para CP437 (DOS/EEUU) ni CP850 (DOS/Europa occidental).
# En cambio, la librería `codecs` incluida con Python sí los soporta.

map_header = Struct(
    "magic" / Const(b"map\x1A\x0D\x0A\0"),
    "version" / Default(Int8ul, 0),
    "width" / Int16ul,
    "height" / Int16ul,
    "code" / Int32ul,
    "description" / Int8ul[32]
)

map_palette = Struct(
    "colors" / Array(256, pal_rgb),
    "ranges" / Array(16, pal_range)
)

map_cpoint = Struct(
    "x" / Int16sl,
    "y" / Int16sl
)

map_file = Struct(
    "header" / map_header,
    "palette" / map_palette,
    "n_cpoints" / Rebuild(Int16ul, len_(this.cpoints)),
    "cpoints" / Array(this.n_cpoints, map_cpoint),
    "pixels" / Array(this.header.width * this.header.height, Int8ul)
)
