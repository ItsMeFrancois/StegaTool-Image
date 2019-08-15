from PIL import Image   #Lesen und Setzen von Pixelwerten
import numpy as np      #Daten in Bit-Array "umwandeln"    
import sys              #Auslesen von uebergebenen Parametern
import os               #Pfad und Dateien auf Existenz pruefen
import math             #Runden bei Berechnung der Pixelkoordinaten
import argparse         #Argumente verwalten


#Funktion zur Berechnung der X- und Y-Koordinate im pixels-Array
#x -> (y,z), mit x ist der x-te Pixel, y ist Spalte und z ist Reihe
def calcXY(x,width):
    row = math.floor(x/width)           #Reihe berechnen(y)
    
    if(x % width == 0):                 
        column = width - 1
        row = row-1
    else:
        column = x  - 1- row * width

    return (column, row)

#Wrapper fuer Image.getPixel() mit obiger Berechnung der Pixelkoordinaten
def getPixel(x,width,image):
    return image.getpixel(calcXY(x,width))

#Setzen/Manipulation eines Pixels
def setPixel(x,rgb,width,pixels):
    column, row = calcXY(x,width)     #Kalkuliere X- und Y-Koordinate des x-ten Pixels im Traeger
    pixels[column, row] = rgb   #Setze an dieser Stelle den uebergebenen RGB-Wert

#Lese Datei ein und erstelle Bitarray aus ebendieser    
def fileToBits(pathToFile):
    if os.path.isfile(pathToFile):
        file = open(pathToFile,"rb")    #Datei Byte fuer Byte einlesen
        raw_bytes = bytearray(file.read())
        file.close()
        
        secret_numpy_bytes = np.array(raw_bytes, dtype="uint8") #Bytearray in Bitarray umwandeln
        secret_bits = list(np.unpackbits(secret_numpy_bytes))
        
        return secret_bits  #Bitarray zurueckgeben
    else:
        return None

def main():
    #Argumente festlegen
    parser = argparse.ArgumentParser(description='Helppage for steganography tool!')

    parser.add_argument('--flip', '-f', help='Flip each stored bit', default=False, nargs='?', const=True, dest='flipped')
    parser.add_argument('--reverse', '-r', help='Store secret bits in reverse order', default=False, nargs='?', const=True, dest='reversed')
    parser.add_argument('--input','-i', help='Path to input file', default=None, nargs='?', dest='inputFile')
    parser.add_argument('--secret','-s', help='Path to secret file', default=None, nargs='?', dest='secretFile')
    parser.add_argument('--output', '-o', help='Path to output file', default=None, nargs='?', dest='outputFile')
    parser.add_argument('--compress','-c', help="Compress output file", default=False, nargs='?', dest="compressed")
    
    
    args = parser.parse_args()          #Argumente parsen

    #Traeger laden
    image = Image.open(args.inputFile)  #Traeger laden
    pixels = image.load()               #Pixel des Traegers in 2-dim-Array sichern

    
    width, height = image.size          #Speichere Breite und Hoehe des Bildes
    
    max_secret_size = width*height*3    #Berechne die maximale Anzahl an Geheimnisbits, die im Traeger gespeichert werden koennen
    
    secret_bits = fileToBits(args.secretFile)   #Bitarray der geladenen Geheimdatei

    if secret_bits is not None:
        #Reverse bit order if the flag was set by the user
        if args.reversed:
            secret_bits = secret_bits[::-1]

        #Flip every bit if the flag was set by the user
        if args.flipped:
            secret_bits = [0 if i == 1 else 1 for i in secret_bits]

        #Anzahl der Bits des Geheimnisses
        bits_count = len(secret_bits)
        
        
        #print("Secret bits:{0}".format(secret_bits))
        #Manipulation der Pixelwerte
        if(bits_count <= max_secret_size):                              #Pruefe ob die Bitsanzahl des Geheimnisses kleiner als die Anzahl der Anzahl an Bits ist, die im Traeger verstecket werden koennen
            for index_pixel in range(0, int(len(secret_bits)/3)):            #Fuer jedes Bit des Geheimnisses...
                #print("{0}. Pixel position:{1}".format(index_pixel+1,calcXY(index_pixel+1,width)))
                pixel = getPixel(index_pixel + 1, width, image)
                new_pixel = list(pixel)[0:3]
                #print("Bits to hide:{0}".format(secret_bits[index_pixel*3:index_pixel*3+3]))
                #print("Before:{0}".format(new_pixel))

                for color_channel in range(0,3):
                    
                    bit = secret_bits[index_pixel*3 + color_channel]
                    if(bit == 1):                                                                  #Wenn das zu speichernde Bit des Geheimnisses gleich 1 ist
                       new_pixel[color_channel] = new_pixel[color_channel] | 1  #xxxx or 00001 = xxx1                 #Logische ODER-Funktion mit dem Gruenwert des Pixels und 0x0...1
                    else:                                                                          #Wenn das zu speichernde Bit des Geheimnisses nicht 1 ist, hier 0
                       new_pixel[color_channel] = new_pixel[color_channel] & 254 #xxxx and 1110 = xxx0
                    
                    
                #print("After:{0}".format(new_pixel))
                setPixel(index_pixel +1, tuple(new_pixel), width, pixels)
            
            if(args.outputFile.split(".")[1] == "png"):
                image.save(args.outputFile, compress_level= 6)
                print("Succesfully saved!\n\nInfo:\n-----\nBytes\nSaved file: {1}\nSaved: {2} Bytes\nMax. Capacity: {0} Bytes".format(max_secret_size / 8,args.inputFile, bits_count/8))
                             
        else:
            print("Medium ist not large enough to store secret data!\nMedium must contain at least {0} pixels".format(bits_count))
    else:
        print("Couldnt fine secret file!")


main()

