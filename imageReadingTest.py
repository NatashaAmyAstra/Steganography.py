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

def decodeBinary(binary):
    result = ''

    # run this next section once for every 8 bit section in given binary string
    for i in range(int(len(binary) / 8)):
        # translate each 8 bit section into an integer value and in turn into a character
        result += chr(int(binary[i * 8 : i * 8 + 8], 2))

    return result


def encodeColor(color, binary):
    # translate the binary into its integer equivalent
    value = int(binary, 2)

    # change color to the nearest multiple of 16 below itself
    # this essentially creates a blank canvas
    color -= color % 16

    # add the value onto the color. color % 16 = value
    color += value

    # make sure the color is within a valid range
    if color > 255:
        color -= 16

    return color


def decodeColor(color):
    # extract encoded value and convert to a 4 bit string
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

    # return indices as a tuple
    return i, j, k

def lengthAllocation(img):
    # writing 4 bits into each R, G and B allows for 12 bits per pixel
    # a character is 8 bits, thus 2 pixels fit exactly 3 characters
    # the maximum number of characters in an image is thus 1.5 * resolution
    maxChrs = 1.5 * len(img) * len(img[0])

    # each image will have a set number of bits allocated to say how long
    # the message encoded in the image is
    # the size of this allocation is the lowest x where 2 ^4x - 1 > 1.5*resolution
    lenAll = 1
    while pow(2, 4 * lenAll) - 1 < maxChrs:
        lenAll += 1

    # due to this allocation, less bits are actually available for text thus
    # maxChrs is slightly decreased
    maxChrs -= math.ceil(lenAll/2)

    return lenAll, maxChrs
    

# encode message into image
def encodeImage(message, imagePath):
    img = iio.imread(imagePath)
    lenAll, maxChr = lengthAllocation(img)

    if len(message) > maxChr:
        print("message too long for this image size,\nplease choose smaller image or shorten your message")
        return

    # before the message, some data is encoded to tell the computer how long the message is
    # space for this is allocated relative to image resolution to ensure we can always decode it
    lengthText = format(len(message), '0'+str(lenAll * 4)+'b')
    binary = lengthText + encodeBinary(message)

    # encode data into image 4 bits at a time
    for x in range(int(len(binary) / 4)):
        # convert the linear x to 3 indices for each unique position
        i, j, k = arrayToThreeIndices(img, x)

        # encode the 4 bits into the color value of the current pixel
        section = binary[x*4 : x*4 +4]
        img[i][j][k] = encodeColor(img[i][j][k], section)

    iio.imwrite(imagePath, img)


def readColors(img, start, end):
    binary = ''

    for x in range(start, end):
        i, j, k = arrayToThreeIndices(img, x)
        binary += decodeColor(img[i][j][k])

    return binary

# extract text from image
def decodeImage(imagePath):
    img = iio.imread(imagePath)
    
    # read how long the message is
    lenAll = lengthAllocation(img)[0]
    messageLen = int(readColors(img, 0, lenAll), 2) * 2
    
    return decodeBinary(readColors(img, lenAll, lenAll + messageLen))


def splitIntoArray(binary, sections, snippit):
    result = []
    
    charPerSection = int(len(binary)/sections)
    charPerSection += -charPerSection % snippit

    for i in range(sections):
        result.append(binary[:charPerSection])
        binary = binary[charPerSection:]

    return result

def txtToImage(textFilePath, imagePath):
    textFile = open(textFilePath, encoding="utf8")
    content = textFile.read()

    img = iio.imread(imagePath)
    lenAll, maxChr = lengthAllocation(img)

    if len(content) > maxChr:
        print("message too long for this image size,\nplease choose smaller image or shorten your message")
        return

    # before the message, some data is encoded to tell the computer how long the message is
    # space for this is allocated relative to image resolution to ensure we can always decode it
    lengthText = format(len(content), '0'+str(lenAll * 4)+'b')
    binary = lengthText + encodeBinary(content)
    textFile.close()

    binary = splitIntoArray(binary, 100, 4)

    for y in binary:
        l = 0
        # encode data into image 4 bits at a time
        for x in range(int(len(y) / 4)):
            # convert the linear x to 3 indices for each unique position
            i, j, k = arrayToThreeIndices(img, int(len(binary[0]) / 4) * l + x)

            # encode the 4 bits into the color value of the current pixel
            section = y[x*4 : x*4 +4]
            img[i][j][k] = encodeColor(img[i][j][k], section)
        l += 1
    iio.imwrite(imagePath, img)
    


