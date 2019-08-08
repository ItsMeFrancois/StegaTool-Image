from PIL import Image   #Lesen und Setzen von Pixelwerten
import numpy as np      #Daten in Bit-Array "umwandeln"    
import sys              #Auslesen von uebergebenen Parametern
import os               #Pfad und Dateien auf Existenz pruefen
import math             #Runden bei Berechnung der Pixelkoordinaten

#Traeger laden
image_path = sys.argv[1]        #Uebergebenen Pfad zum Traeger sichern
image = Image.open(image_path)  #Traeger laden
pixels = image.load()           #Pixel des Traegers in 2-dim-Array sichern

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
def getPixel(x,width):
    return image.getpixel(calcXY(x,width))

#Setzen/Manipulation eines Pixels
def setPixel(x,rgb,width):
    column, row = calcXY(x,width)     #Kalkuliere X- und Y-Koordinate des x-ten Pixels im Traeger
    pixels[column, row] = rgb   #Setze an dieser Stelle den uebergebenen RGB-Wert

#Lese Datei ein und erstelle Bitarray aus ebendieser    
def fileToBits(pathToFile):
    if os.path.isfile(pathToFile):
        file = open(pathToFile,"rb")    #Datei Byte fuer Byte einlesen
        raw_bytes = bytearray(file.read())
        file.close()
        
        secret_numpy_bytes = np.array(raw_bytes, dtype="uint8") #Bytearray in Bitarray umwandeln
        secret_bits = np.unpackbits(secret_numpy_bytes)
        
        return secret_bits  #Bitarray zurueckgeben
    else:
        return None

def main():
    #Speichere Breite und Hoehe des Bildes
    width, height = image.size
    
    #Berechne die maximale Anzahl an Geheimnisbytes, die im Traeger gespeichert werden koennen
    #Da hier jeweils ein Bit des Geheimnisses in einem Pixel gespeichert wird, koennen maximal
    #Hoehe*Breite Bits im Bild gespeichert werden, also (Hoehe*Breite)/8 Bytes
    max_secret_size = (width*height)
    
    #Sichere uebergebenen Pfad zur Geheimdatei
    secret= sys.argv[2]
    
    #Bitarray der geladenen Geheimdatei
    secret_bits = fileToBits(secret)
    if secret_bits is not None:
        #Anzahl der Bits des Geheimnisses
        bits_count = len(secret_bits)
    
        #Gebe Anzahl der Bits des Geheimnisses aus
        print("Secret bits: {0}".format(secret_bits))
    
        #Manipulation der Pixelwerte
        if(bits_count <= max_secret_size):                              #Pruefe ob die Bitsanzahl des Geheimnisses kleiner als die Anzahl der Anzahl an Bits ist, die im Traeger verstecket werden koennen
            for i,bit in enumerate(secret_bits):                        #Fuer jedes Bit des Geheimnisses...
                pixel = getPixel(i+1,width)                                   #Ermittle RGB-Werte des i+1 Pixels (i startet bei 0)
                R = pixel[0]
                G = pixel[1]
                B = pixel[2]
                new_G = 0                                          #Zwischenspeicher fuer neuen Gruenwert nach Manipulation des LSB (Least Significant Bit)
            
                if(bit == 1):                                           #Wenn das zu speichernde Bit des Geheimnisses gleich 1 ist
                    new_G = G | 1  #xxxx or 00001 = xxx1                #Logische ODER-Funktion mit dem Gruenwert des Pixels und 0x0...1
                else:                                                   #Wenn das zu speichernde Bit des Geheimnisses nicht 1 ist, hier 0
                    new_G = G & 254 #xxxx and 1110 = xxx0
            
                newRGB = (R,new_G,B)                                                        #Neues RGB-Tupel erstellen
                setPixel(i+1, newRGB,width)                                                       #Generiertes Tupel mit modifiziertem Gruenwert in das Bild im Speicher setzen
        
            image.save("{0}_hidden.png".format(sys.argv[1].split(".")[0]))                  #Sichere das bearbeitete Image mit dem Zusatz "_hidden" mit dem selben Format
        else:
            print("Medium ist not large enough to store secret data!\nMedium must contain at least {0} pixels".format(bits_count))
    else:
        print("Couldnt fine secret file!")


main()

