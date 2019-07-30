import sys
import numpy as np
import math
from PIL import Image

def calcXY(x, width):
    row = math.floor(x/width)
    
    if(x % width == 0):
        column = width - 1
        row = row-1
    else:
        column = x  - 1- row * width

    return (column, row)

def getPixel(img, x, width):
    return image.getpixel(calcXY(x, width))

if (sys.argv[1] == 'read'):
    with open("{0}_rawRGB.txt".format(sys.argv[2].split(".")[0]),"w") as f:
        im = Image.open(sys.argv[2])
        pixels = list(im.getdata())
        for pixel in pixels:
            f.write("{0}\n".format(str(pixel)))

elif (sys.argv[1] == 'check'):
    f1 = open(sys.argv[2],"r")
    f2 = open(sys.argv[3],"r")
    l1 = f1.readlines()
    l2 = f2.readlines()

    for index in range(0,len(l1)):
        if(l1[index] != l2[index]):
            print("Ungleich!")
            sys.exit()
    print("Gleich!")
elif(sys.argv[1] == 'extract'):
    #Anzahl an Bits, die zu extrahieren sind
    bits_to_read = int(sys.argv[3]) * 8
    image = Image.open(sys.argv[2])
    width, height = image.size
    bits = []

    for i in range(1, bits_to_read+1):
        pixel = getPixel(image, i, width)
        gValue = np.uint8(pixel[1])
        gValue_bits = np.unpackbits(gValue)
        bits.append(gValue_bits[7])
    
   
    for i in range(0,len(bits), 8):
        value = 0
        for o,bit in enumerate(bits[i:i+8]):
            #print(o)
            value += pow(2,7-o) * bit
        print(chr(value))
