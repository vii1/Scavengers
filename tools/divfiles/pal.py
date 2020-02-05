from construct import *

pal_header = Struct(
    "magic" / Const(b'pal\x1A\x0D\x0A\0'),
    "version" / Default(Int8ul, 0)
)

pal_rgb = Struct(
    "r" / Default(Int8ul, 0),
    "g" / Default(Int8ul, 0),
    "b" / Default(Int8ul, 0),
    Check(this.r < 64 and this.g < 64 and this.b < 64)
)

pal_range = Struct(
    "n_colors" / Default(Int8ul, 16),
    "type" / Default(Enum(Int8ul,
        direct = 0,
        edit1 = 1,
        edit2 = 2,
        edit4 = 4,
        edit8 = 8
    ), 'direct'),
    "fixed" / Default(Flag, False),
    "black" / Default(Int8ul, 0),
    "colors" / Default(Array(32, Int8ul), lambda this: [this._index * 16 + x if x<16 else 0 for x in range(32)])
)

pal_file = Struct(
    "header" / pal_header,
    "colors" / Default(Array(256, pal_rgb), [{}]*256),
    "ranges" / Default(Array(16, pal_range), [{}]*16)
)
