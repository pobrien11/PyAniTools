import multiprocessing
import OpenEXR
import Imath
import array
from PIL import Image
import time

def worker(procnum, image_path, channel_names, size, color_transform, return_dict):
    '''worker function'''
    img_file = OpenEXR.InputFile(image_path)


 # single channel layer, put same value in red, green, and blue
    if len(channel_names) == 1:
        r_channel = channel_names[0]
        g_channel = channel_names[0]
        b_channel = channel_names[0]
    # multi channel layer
    else:
        # check if RGB which needs different handling
        r_channel = channel_names[0]
        g_channel = channel_names[1]
        b_channel = channel_names[2]


    (r, g, b) = img_file.channels([r_channel, g_channel, b_channel], Imath.PixelType(Imath.PixelType.FLOAT))

    red = array.array('f', r)
    green = array.array('f', g)
    blue = array.array('f', b)

    # apply color transform (sRGB) if option is True
    if color_transform:
        pass
        #red, green, blue = pyani.core.util.convert_to_sRGB(red, green, blue)

    # convert to rgb 8-bit image
    rgbf = [Image.frombytes("F", size, red.tostring())]
    rgbf.append(Image.frombytes("F", size, green.tostring()))
    rgbf.append(Image.frombytes("F", size, blue.tostring()))
    rgb8 = [im.convert("L") for im in rgbf]

    img_file.close()

    return_dict[procnum] = Image.merge("RGB", rgb8)

if __name__ == '__main__':
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []

    layers = ['RGB', 'N', 'P', 'Z', 'albedo', 'crypto_object', 'crypto_object00', 'crypto_object01', 'crypto_object02', 'diffuse', 'diffuse_albedo', 'emission', 'specular', 'sss']

    channels = [['R', 'G', 'B'],
                ['N.X', 'N.Y', 'N.Z'],
                ['P.X', 'P.Y', 'P.Z'],
                ['Z'],
                ['albedo.R', 'albedo.G', 'albedo.B'],
                ['crypto_object.R', 'crypto_object.G', 'crypto_object.B'],
                ['crypto_object00.R', 'crypto_object00.G', 'crypto_object00.B'],
                ['crypto_object01.R', 'crypto_object01.G', 'crypto_object01.B'],
                ['crypto_object02.R', 'crypto_object02.G', 'crypto_object02.B'],
                ['diffuse.R', 'diffuse.G', 'diffuse.B'],
                ['diffuse_albedo.R', 'diffuse_albedo.G', 'diffuse_albedo.B'],
                ['emission.R', 'emission.G', 'emission.B'],
                ['specular.R', 'specular.G', 'specular.B'],
                ['sss.R', 'sss.G', 'sss.B']]


    t0 = time.time()
    for i in range(0, len(layers)):
        p = multiprocessing.Process(target=worker, args=(i, "C:\Users\Patrick\Desktop\\test.exr", channels[i], (1920, 1080), True, return_dict ))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
    t1 = time.time()
    print "time:" , t1-t0
    print return_dict.values()