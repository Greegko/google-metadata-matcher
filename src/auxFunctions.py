import os
import time
from datetime import datetime
import piexif
from fractions import Fraction


# Credit: https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r", upLines = 0):
    UP = "\x1B[" + str(upLines + 1) + "A"

    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)

        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        print(UP)
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

# Function to search media associated to the JSON
def searchMedia(path, title, editedWord):
    title = fixTitle(title)

    (file_name, ext) = os.path.splitext(title)

    possible_titles = [
        title,
        str(file_name + "-" + editedWord + "." + ext),
        str(file_name + "(1)." + ext),
    ]

    for title in possible_titles:
        filepath = os.path.join(path, title)

        if os.path.exists(filepath):
            return filepath

# Supress incompatible characters
def fixTitle(title):
    return str(title).replace("%", "").replace("<", "").replace(">", "").replace("=", "").replace(":", "").replace("?","").replace(
        "¿", "").replace("*", "").replace("#", "").replace("&", "").replace("{", "").replace("}", "").replace("\\", "").replace(
        "@", "").replace("!", "").replace("¿", "").replace("+", "").replace("|", "").replace("\"", "").replace("\'", "")

# Recursive function to search name if its repeated
def checkIfSameName(title, titleFixed, matchedFiles, recursionTime):
    if titleFixed in matchedFiles:
        (file_name, ext) = os.path.splitext(titleFixed)
        titleFixed = file_name + "(" + str(recursionTime) + ")" + "." + ext
        return checkIfSameName(title, titleFixed, matchedFiles, recursionTime + 1)
    else:
        return titleFixed

def setFileCreationTime(filepath, timeStamp):
    date = datetime.fromtimestamp(timeStamp)
    modTime = time.mktime(date.timetuple())
    os.utime(filepath, (modTime, modTime))

def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value - deg) * 60
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    return (deg, min, sec, loc_value)


def change_to_rational(number):
    """convert a number to rational
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)

def set_geo_exif(exif_dict, lat, lng, altitude):
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    altitudeRef = 1 if altitude > 0 else 0 

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: altitudeRef,
        piexif.GPSIFD.GPSAltitude: change_to_rational(round(abs(altitude), 2)),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng,
    }

    exif_dict['GPS'] = gps_ifd

def set_date_exif(exif_dict, timestamp):
    dateTime = datetime.fromtimestamp(timestamp).strftime("%Y:%m:%d %H:%M:%S")
    exif_dict['0th'][piexif.ImageIFD.DateTime] = dateTime
    exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = dateTime
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = dateTime

def adjust_exif(exif_info, metadata):
    timeStamp = int(metadata['photoTakenTime']['timestamp'])

    exif_dict = piexif.load(exif_info)

    del exif_dict["thumbnail"]

    lat = metadata['geoData']['latitude']
    lng = metadata['geoData']['longitude']
    altitude = metadata['geoData']['altitude']

    set_date_exif(exif_dict, timeStamp)
    set_geo_exif(exif_dict, lat, lng, altitude)

    return piexif.dump(exif_dict)
