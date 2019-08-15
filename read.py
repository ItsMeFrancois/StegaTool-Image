import sys
import numpy as np
import math
from PIL import Image
import argparse
import bitarray

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

#Argumente festlegen
parser = argparse.ArgumentParser(description='Helppage for steganography tool!')

parser.add_argument('--read', '-r', help='Read', default=False, nargs='?', const=True, dest='read')
parser.add_argument('--count', '-c', help='How many bytes to read', default=False, nargs='?', const=True, dest='count')
parser.add_argument('--inputfile', '-i', help='Path to inputfile', default=None, nargs='?', dest='input_file')
parser.add_argument('--outputfile', '-o', help='Path to outputfile', default=None, nargs='?', dest='output_file')


args = parser.parse_args()

if args.read:
    bits_to_read = int(args.count) * 8
    image = Image.open(args.input_file)
    width, height = image.size

    bits = []

    for index in range(0, bits_to_read,3):
        #print("{0}. Pixel position:{1}".format(index+1,calcXY(index+1,width)))
        pixel = getPixel(image, (index/3)+1, width)
        #print(pixel)
        for color_channel in range(0,3):
            value = np.uint8(pixel[color_channel])
            value_bits = np.unpackbits(value)
            bits.append(value_bits[7])
    
    bits = bitarray.bitarray(bits)
    with open(args.output_file, 'wb') as fh:
        bits.tofile(fh)
    
