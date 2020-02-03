from construct import *
from .map import map_palette, map_cpoint

# Nota: las cadenas mejor (des)codificarlas aparte ya que Construct no trae
# soporte para CP437 (DOS/EEUU) ni CP850 (DOS/Europa occidental).
# En cambio, la librería `codecs` incluida con Python sí los soporta.

fpg_header = Struct(
    "magic" / Const(b"fpg\x1A\x0D\x0A\0"),
    "version" / Default(Int8ul, 0)
)

fpg_palette = map_palette

fpg_map = Struct(
    "code" / Int32ul,
    "length" / Rebuild(Int32ul, len_(this)),
    "description" / FixedSized(32, NullStripped(GreedyBytes)),
    "filename" / FixedSized(12, NullStripped(GreedyBytes)),
    "width" / Int32ul,
    "height" / Int32ul,
    "n_cpoints" / Rebuild(Int32ul, len_(this.cpoints)),
    "cpoints" / Array(this.n_cpoints, map_cpoint),
    "pixels" / Array(this.width * this.height, Int8ul)
)

fpg_file = Struct(
    "header" / fpg_header,
    "palette" / fpg_palette,
    "maps" / GreedyRange(fpg_map)
)
