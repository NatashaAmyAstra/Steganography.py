import numpy as np
import imageio.v3 as iio
import math
import random

# DECODING IMAGE:
# RGB values hold 4 encoded bits of binary
# R, G or B value % 20 = our encoded value

# translate text to a long string of binary
def encodeBinary(message):
    return ''.join(format(ord(i), '08b') for i in message)

# translate binary to text
def decodeBinary(message):    
    result = ''
    for i in range(int(len(message) / 8)):
        result += chr(int(message[i * 8 : i * 8 + 8], 2))

    return result


def encodeColor(color, binary):
    value = int(binary, 2)
    color -= color % 16
    color += value

    if color > 255:
        color -= 16

    return color

def decodeColor(color):
    return format(color % 16, '04b')

def arrayToThreeIndices(arr, x):
    # a, b and c represent the length of each depth of the array
    a = len(arr)
    b = len(arr[0])
    c = len(arr[0][0])

    # uses a, b and c to calculate each index
    i = math.floor((x/(b * c)) % a)
    j = math.floor((x/c) % b)
    k = x % c

    return i, j, k

def lengthAllocation(img){
    maxChrs = 1.5 * len(img) * len(img[0])
    lenAll = 1
    while pow(2, 4 * lenAll) - 1 < maxChrs:
        lenAll += 1

    maxChrs -= math.ceil(lenAll/2)

    return lenAll, maxChrs
    

# encode message into image
def encodeImage(message, imagePath):
    binary = encodeBinary(message)

    img = iio.imread(imagePath)

    for x in range(int(len(binary) / 4)):
        i, j, k = arrayToThreeIndices(img, x)

        # which section of binary is going to be encoded next
        section = binary[x*4 : x*4 +4]
        img[i][j][k] = encodeColor(img[i][j][k], section)

    iio.imwrite(imagePath, img)

# extract text from image
def decodeImage(imagePath, length):
    img = iio.imread(imagePath)
    result = ''

    for x in range(length):
        i, j, k = arrayToThreeIndices(img, x)
        result += decodeColor(img[i][j][k])

    return decodeBinary(result)
