import os
import warnings
import argparse

from PIL import Image

# Colors for both irc and terminal. Adjust the rgb value to match better if needed
COLORS = [
#   [renderIRC    RGB             Term    Name]
    [0,     (255,255,255),  '97',   'white'],
    [1,     (0,0,0),        '30',   'black'],
    [2,     (0,0,127),      '34',   'blue'],
    [3,     (0,147,0),      '32',   'green'],
    [4,     (255,0,0),      '91',   'light red'],
    [5,     (127,0,0),      '31',   'brown'],
    [6,     (156,0,156),    '35',   'purple'],
    [7,     (252,127,0),    '33',   'orange'],
    [8,     (255,255,0),    '93',   'yellow'],
    [9,     (0,252,0),      '92',   'light green'],
    [10,    (0,147,147),    '36',   'cyan'],
    [11,    (0,255,255),    '96',   'light cyan'],
    [12,    (0,0,252),      '94',   'light blue'],
    [13,    (255,0,255),    '95',   'pink'],
    [14,    (127,127,127),  '90',   'grey'],
    [15,    (210,210,210),  '37',   'light grey']
]

# Converts an image file into lines of braille unicode.
#   cutoff      dictates the contrast level for when not to render pixels
#                   Cutoff is based on a blackbackground, so it won't render pixels darker than the value
#   size        is a modifier for the overall size
#   doColor     says if we want color escapes in our unicode
#   renderIRC   says if we want to use IRC color escapes instead of ansi escapes
#   invert      says if we want to invert the colors in the image
def convert(img, doColor=True, renderIRC=True, cutoff=50, size=1.0, invert=False, alphaColor=(0,0,0)):
    i = Image.open(img)

    WIDTH = int(90*size)
    HIGHT = int(40*size)

    # Resize the image to fix bounds
    s = i.size
    if s[0]==0 or s[1]==0 or (float(s[0])/float(WIDTH))==0 or (float(s[1])/float(HIGHT))==0:
        return []
    ns = (WIDTH,int(s[1]/(float(s[0])/float(WIDTH))))
    if ns[1]>HIGHT:
        ns = (int(s[0]/(float(s[1])/float(HIGHT))),HIGHT)

    i2 = i.resize(ns)

    bimg = []


    for r in range(0,i2.size[1],4):
        line = u''
        lastCol = -1
        for c in range(0,i2.size[0],2):
            val = 0
            i = 0
            cavg = [0,0,0]
            pc = 0

            for ci in range(0,4):
                for ri in range(0,3 if ci<2 else 1):
                    # Convert back for the last two pixels
                    if ci>=2:
                        ci-=2
                        ri=3

                    # Retrieve the pixel data
                    if c+ci<i2.size[0] and r+ri<i2.size[1]:
                        p = i2.getpixel((c+ci,r+ri))
                        alpha = p[3] if len(p)>3 else 1
                        if invert and alpha>0:
                            p = map(lambda x: 255-x, p)
                        elif alpha==0:
                            p = alphaColor
                    else:
                        p = (0,0,0)

                    # Check the cutoff value and add to unicode value if it passes
                    luma = (0.2126*float(p[0]) + 0.7152*float(p[1]) + 0.0722*float(p[2]))
                    pv = sum(p[:3])
                    if luma > cutoff:
                        val+=1<<i
                        cavg = map(sum,zip(cavg,p))
                        pc+=1
                    i += 1

            if doColor and pc>0:
                # Get the average of the 8 pixels
                cavg = map(lambda x:x/pc,cavg)

                # Find the closest color with geometric distances
                colorDist = lambda c:sum(map(lambda x:(x[0]-x[1])**2,zip(cavg,c[1])))
                closest = min(COLORS, key=colorDist)

                if closest[0]==1 or lastCol==closest[0]:
                    # Check if we need to reset the color code
                    if lastCol!=closest[0] and lastCol!=-1:
                        line+='\x03' if renderIRC else '\033[0m'
                    line += unichr(0x2800+val)
                else:
                    # Add the color escape to the first character in a set of colors
                    if renderIRC:
                        line += ('\x03%u'%closest[0])+unichr(0x2800+val)
                    else:
                        line += ('\033[%sm'%closest[2])+unichr(0x2800+val)
                lastCol = closest[0]
            else:
                # Add the offset from the base braille character
                line += unichr(0x2800+val)
        bimg.append(line)
    return bimg
    

if __name__=='__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('file', help='The image file to render')
    ap.add_argument('-c',type=int,default=100, help='The luma cutoff amount, from 0 to 255. Default 50')
    ap.add_argument('-s', type=float, default=1.0, help='Size modifier. Default 1.0x')
    ap.add_argument('--nocolor', action="store_true", default=False, help='Don\'t use color')
    ap.add_argument('--irc', action="store_true", default=False, help='Use IRC color escapes')
    ap.add_argument('--invert', action="store_true", default=False, help='Invert the image colors')
    ap.add_argument('--background', default='black', help='The color to display for full alpha transparency')
    args = ap.parse_args()

    alphaColor = (0,0,0)
    for c in COLORS:
        if c[3].lower() == args.background:
            alphaColor = c[1]
            break
    print alphaColor

    for u in convert(args.file,doColor=not args.nocolor, renderIRC=args.irc, cutoff=args.c, size=args.s, invert=args.invert, alphaColor=alphaColor):
        print u.encode('utf-8')
