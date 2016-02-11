# Image-To-Braille
Covers a given image to a unicode version using braille characters and color escapses.

## Basic Example
![Original](https://upload.wikimedia.org/wikipedia/commons/e/ee/GNU%2BLinux.png)

`python braille.py /tmp/it-is-GNU-SLASH-linux.png -s 4 -c 50 --background white`

![After](http://puu.sh/n4m1L/e54e4750a0.png)

## Usage
```
usage: braille.py [-h] [-c C] [-s S] [--nocolor] [--irc] [--invert]
                  [--background BACKGROUND]
                  file

positional arguments:
  file                  The image file to render

optional arguments:
  -h, --help            show this help message and exit
  -c C                  The luma cutoff amount, from 0 to 255. Default 50
  -s S                  Size modifier. Default 1.0x
  --nocolor             Don't use color
  --irc                 Use IRC color escapes
  --invert              Invert the image colors
  --background BACKGROUND
                        The color to display for full alpha transparency
```
