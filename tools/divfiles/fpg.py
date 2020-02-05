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
    "length_pos" / Tell,
    "length" / Padding(4),
    "description" / FixedSized(32, NullStripped(GreedyBytes)),
    "filename" / FixedSized(12, NullStripped(GreedyBytes)),
    "width" / Int32ul,
    "height" / Int32ul,
    "n_cpoints" / Rebuild(Int32ul, len_(this.cpoints)),
    "cpoints" / Array(this.n_cpoints, map_cpoint),
    "pixels" / HexDump(Array(this.width * this.height, Int8ul)),
    "end_pos" / Tell,
    "total_length" / Computed(lambda this: this.end_pos - this.length_pos + 4),
    "length" / Pointer(this.length_pos, Rebuild(Int32ul, this.total_length))
)

fpg_file = Struct(
    "header" / fpg_header,
    "palette" / fpg_palette,
    "maps" / GreedyRange(fpg_map)
)
