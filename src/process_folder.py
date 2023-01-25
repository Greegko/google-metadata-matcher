import os
from auxFunctions import *
import json
from PIL import Image

def processFolder(rootFolder, editedWord, optimize, replace_original, outFolder):
    piexifCodecs = [k.casefold() for k in ['TIF', 'TIFF', 'JPEG', 'JPG']]

    matchedFiles = []  # array with names of all the media already matched
    errorCounter = 0
    successCounter = 0

    files = list(os.scandir(rootFolder))  #Convert iterator into a list to sort it
    files.sort(key=lambda s: len(s.name)) #Sort by length to avoid name(1).jpg be processed before name.jpg

    if not replace_original and not os.path.exists(outFolder):
        os.mkdir(outFolder)

    for file in files:
        if file.is_file() and file.name.endswith(".json"):  # Check if file is a JSON
            with open(file, encoding="utf8") as f:  # Load JSON into a var
                data = json.load(f)

            titleOriginal = data['title']  # Store metadata into vars

            try:
                filepath = searchMedia(rootFolder, titleOriginal, matchedFiles, editedWord)
            except Exception as e:
                print(titleOriginal + " not found")
                errorCounter += 1
                continue

            timeStamp = int(data['photoTakenTime']['timestamp'])  # Get creation time
            print('File:', filepath)

            if titleOriginal.rsplit('.', 1)[1].casefold() in piexifCodecs:  # If EXIF is supported
                try:
                    im = Image.open(filepath, mode="r")
                    os.replace(filepath, filepath.rsplit('.', 1)[0] + ".jpg")
                    filepath = filepath.rsplit('.', 1)[0] + ".jpg"

                    if replace_original:
                        im.save(filepath, quality=optimize)
                        os.remove(file.path)
                        setFileCreationTime(filepath, timeStamp)
                    else:
                        newFilePath = os.path.join(outFolder, titleOriginal)
                        im.save(newFilePath, quality=optimize)
                        setFileCreationTime(newFilePath, timeStamp)

                except ValueError as e:
                    print("Error converting to JPG in " + titleOriginal)
                    print(e)
                    errorCounter += 1
                    continue

                try:
                    set_EXIF(filepath, data['geoData']['latitude'], data['geoData']['longitude'], data['geoData']['altitude'], timeStamp)

                except Exception as e:  # Error handler
                    print("Inexistent EXIF data for " + filepath)
                    print(e)
                    errorCounter += 1
                    continue

            matchedFiles.append(titleOriginal)
            successCounter += 1

    print('Process finished')
    print('Success', successCounter)
    print('Failed', errorCounter)

