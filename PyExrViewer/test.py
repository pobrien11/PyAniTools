import OpenEXR
import Imath
import sys, array


def Put_Exr_Data(_ExrFile, channels_name):
    file = OpenEXR.InputFile(_ExrFile)
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    dw = file.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    if channels_name == 'RGB':
        RedStr, GreenStr, BlueStr = file.channels(["R","G","B"], pt)
        """
        RedStr = file.channel("R", pt)
        GreenStr = file.channel("G", pt)
        BlueStr = file.channel("B", pt)
        """
    else:
        RedStr = file.channel(channels_name, pt)
        GreenStr = file.channel(channels_name, pt)
        BlueStr = file.channel(channels_name, pt)

    print len(RedStr)
    Red = array.array('f', RedStr)
    print len(Red)
    Green = array.array('f', GreenStr)
    Blue = array.array('f', BlueStr)
    return (Red, Green, Blue, size)


def EncodeToSRGB(v):
    if (v <= 0.0031308):
        return (v * 12.92) * 255.0
    else:
        return (1.055 * (v ** (1.0 / 2.2)) - 0.055) * 255.0


def ConvertSRGB(Red, Green, Blue):
    rgb_size = range(len(Red))
    for I in rgb_size:
        Red[I] = EncodeToSRGB(Red[I])
        Green[I] = EncodeToSRGB(Green[I])
        Blue[I] = EncodeToSRGB(Blue[I])
    return Red, Green, Blue


def format(d, tab=0):
    s = ['{\n']
    for k, v in d.items():
        if isinstance(v, dict):
            v = format(v, tab + 1)
        else:
            v = repr(v)

        s.append('%s%r: %s,\n' % ('  ' * tab, k, v))
    s.append('%s}' % ('  ' * tab))
    return ''.join(s)

from PIL import Image, ImageDraw
import sys, array


import time

t0 = time.time()
# 0-Red, 1-Green, 2-Blue, 3-Size, 4-Header data
_EXR_data_= Put_Exr_Data("C:\Users\Patrick\Desktop\\1krgba.exr","RGB")

t1 = time.time()

print t1-t0
ConvertSRGB(_EXR_data_[0],_EXR_data_[1],_EXR_data_[2])

rgbf = [Image.frombytes("F", _EXR_data_[3], _EXR_data_[0].tostring())]
rgbf.append(Image.frombytes("F", _EXR_data_[3], _EXR_data_[1].tostring()))
rgbf.append(Image.frombytes("F", _EXR_data_[3], _EXR_data_[2].tostring()))

rgb8 = [im.convert("L") for im in rgbf]

exrimage = Image.merge("RGB", rgb8)

exrimage.show()
