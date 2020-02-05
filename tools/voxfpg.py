from wand.image import Image
from wand.display import display
from divmagick import *

def _readpy(file: str):
    vars = {}
    exec(open(file).read(), vars)
    return vars


def voximgs(infile: str):
    data = _readpy(infile)
    width = data['widthGrid'] + 1
    depth = data['depthGrid'] + 1
    height = data['heightGrid'] + 1
    buffers = [[0 for x in range(width * depth * 4)] for y in range(height)]
    for v in data['lookup']:
        if 'color' in v:
            color = data['pallette'][v['color']]
            pixel = (v['z'] * width + v['x']) * 4
            buffers[v['y']][pixel:pixel + 4] = [color['red'], color['green'], color['blue'], 255]
    imgs = []
    for buf in buffers:
        im = Image(width=width, height=depth, colorspace='rgb')
        im.import_pixels(channel_map='RGBA', data=bytes(buf))
        imgs.append(im)
    return imgs


def vox2fpg(infile: str, outfile: str, descpattern=None, colors=256, dither=False):
    import os.path
    from sys import stdout
    print(infile,'->',outfile,'...',end='')
    stdout.flush()
    imgs = voximgs(infile)
    imgs, impalette = div_reduce_images(imgs, colors, dither)
    # for i in range(len(imgs)):
    #     imgs[i].save(filename="r:\\temp%03d.png" % i)
    if not descpattern:
        descpattern = os.path.basename(infile) + " (%02d)"
    buf = div_fpg(imgs, impalette, descpattern)
    with open(outfile, 'wb') as f:
        f.write(buf)
    print('ok')

# if __name__ == '__main__':
#     imgs = voximgs('../objetos/prota/prota.py')
#     imgs, impalette = div_reduce_images(imgs)
#     for i in range(len(imgs)):
#         imgs[i].save(filename="r:\\temp%03d.png" % i)

#     buf = div_fpg(imgs, impalette, "Prota (%02d)")
#     #with open('../objetos/prota/prota.fpg', 'wb') as f:
#     with open('r:\\prota.fpg', 'wb') as f:
#         f.write(buf)
