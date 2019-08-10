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
    
    max_secret_size = (width*height)    #Berechne die maximale Anzahl an Geheimnisbytes, die im Traeger gespeichert werden koennen
    
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
    
        #Manipulation der Pixelwerte
        if(bits_count <= max_secret_size):                              #Pruefe ob die Bitsanzahl des Geheimnisses kleiner als die Anzahl der Anzahl an Bits ist, die im Traeger verstecket werden koennen
            for i,bit in enumerate(secret_bits):                        #Fuer jedes Bit des Geheimnisses...
                pixel = getPixel(i+1,width,image)                       #Ermittle RGB-Werte des i+1 Pixels (i startet bei 0)
                R = pixel[0]
                G = pixel[1]
                B = pixel[2]
                new_G = 0                                               #Zwischenspeicher fuer neuen Gruenwert nach Manipulation des LSB (Least Significant Bit)
            
                if(bit == 1):                                           #Wenn das zu speichernde Bit des Geheimnisses gleich 1 ist
                    new_G = G | 1  #xxxx or 00001 = xxx1                #Logische ODER-Funktion mit dem Gruenwert des Pixels und 0x0...1
                else:                                                   #Wenn das zu speichernde Bit des Geheimnisses nicht 1 ist, hier 0
                    new_G = G & 254 #xxxx and 1110 = xxx0
            
                newRGB = (R,new_G,B)                                                        #Neues RGB-Tupel erstellen
                setPixel(i+1, newRGB,width,pixels)                                                       #Generiertes Tupel mit modifiziertem Gruenwert in das Bild im Speicher setzen
            
                if(args.outputFile.split(".")[1] == "png"):
                    image.save(args.outputFile, compress_level= 1) 
                             
        else:
            print("Medium ist not large enough to store secret data!\nMedium must contain at least {0} pixels".format(bits_count))
    else:
        print("Couldnt fine secret file!")


main()

