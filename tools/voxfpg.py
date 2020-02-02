from PIL import Image

def _readpy(file : str):
    vars = {}
    exec(open(file).read(), vars)
    return vars

def voxfpg(infile:str, outfile:str):
    data = _readpy(infile)
    imgs = [Image.new('RGBA', (data['widthGrid']+1, data['depthGrid']+1), (0,0,0,0)) for i in range(data['heightGrid']+1)]
    for v in data['lookup']:
        if 'color' in v:
            color = data['pallette'][v['color']]
            imgs[v['y']].putpixel((v['x'],v['z']), (color['red'], color['green'], color['blue'], 255))
    for i in range(len(imgs)):
        imgs[i].save("r:\\temp%03d.png" % i)

if __name__=='__main__':
    voxfpg('../objetos/prota/prota.py','')