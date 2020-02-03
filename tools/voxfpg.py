from PIL import Image
from .divpil import div_pal

def _readpy(file : str):
    vars = {}
    exec(open(file).read(), vars)
    return vars

def voximgs(infile:str):
    data = _readpy(infile)
    imgs = [Image.new('RGBA', (data['widthGrid']+1, data['depthGrid']+1), (0,0,0,0)) for i in range(data['heightGrid']+1)]
    for v in data['lookup']:
        if 'color' in v:
            color = data['pallette'][v['color']]
            imgs[v['y']].putpixel((v['x'],v['z']), (color['red'], color['green'], color['blue'], 255))
    return imgs

def quantize_imgs(imgs:list, colors=256, dither=False):
    margin = 5
    totalwidth = sum([i.width for i in imgs]) + margin * (len(imgs) + 1)
    totalheight = max([i.height for i in imgs]) + margin * 2
    bigimg = Image.new('RGBA', (totalwidth, totalheight), (0,0,0,0))
    x = margin
    for i in imgs:
        bigimg.paste(i, (x, margin))
        x += i.width + margin
    bigimg = bigimg.quantize(colors, dither=Image.FLOYDSTEINBERG if dither else 0)
    newimgs = []
    x = margin
    for i in imgs:
        img = bigimg.crop((x, margin, x + i.width, margin + i.height))
        newimgs.append(img)
        x += i.width + margin
    return newimgs

if __name__=='__main__':
    imgs = voximgs('../objetos/prota/prota.py')
    imgs = quantize_imgs(imgs, 256)
    for i in range(len(imgs)):
        imgs[i].save("r:\\temp%03d.png" % i)
