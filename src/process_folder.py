import os
from auxFunctions import *
import json
from PIL import Image
from pillow_heif import register_heif_opener
import shutil

register_heif_opener()

CLR = "\x1B[0K"
CURSOR_UP_FACTORY = lambda upLines: "\x1B[" + str(upLines) + "A"
CURSOR_DOWN_FACTORY = lambda upLines: "\x1B[" + str(upLines) + "B"

OrientationTagID = 274

piexifCodecs = [k.casefold() for k in ["TIF", "TIFF", "JPEG", "JPG", "HEIC", "PNG"]]


def get_images_from_folder(folder: str, edited_word: str):
    files: list[tuple[str, str]] = []
    folder_entries = list(os.scandir(folder))

    for entry in folder_entries:
        if entry.is_dir():
            files = files + get_images_from_folder(entry.path, edited_word)
            continue

        if entry.is_file():
            (file_name, ext) = os.path.splitext(entry.name)

            if ext == ".json" and file_name != "metadata":
                file = searchMedia(folder, file_name, edited_word)
                files.append((entry.path, file))

    return files


def get_output_filename(root_folder, out_folder, image_path):
    (image_name, ext) = os.path.splitext(os.path.basename(image_path))
    new_image_name = image_name + ".jpg"
    image_path_dir = os.path.dirname(image_path)
    relative_to_new_image_folder = os.path.relpath(image_path_dir, root_folder)
    return os.path.join(out_folder, relative_to_new_image_folder, new_image_name)


def processFolder(
    root_folder: str, edited_word: str, optimize: int, out_folder: str, max_dimension
):
    errorCounter = 0
    successCounter = 0

    images = get_images_from_folder(root_folder, edited_word)

    print("Total images found:", len(images))

    failed_folder = os.path.join(
        out_folder, "failed"
    )  # Create the path for the 'failed' folder
    if not os.path.exists(failed_folder):
        os.makedirs(failed_folder)  # Ensure the 'failed' folder exists

    for entry in progressBar(images, upLines=2):
        metadata_path = entry[0]
        image_path = entry[1]

        print("\n", "Current file:", image_path, CLR)

        if not image_path:
            print(
                CURSOR_UP_FACTORY(2),
                "Missing image for:",
                metadata_path,
                CLR,
                CURSOR_DOWN_FACTORY(2),
            )

            errorCounter += 1
            failed_metadata_path = os.path.join(
                failed_folder, os.path.relpath(metadata_path, root_folder)
            )
            dir = os.path.dirname(failed_metadata_path)
            if os.path.exists(metadata_path):
                if not os.path.exists(dir):
                    os.makedirs(dir)  # Create subfolder
                shutil.copy2(
                    metadata_path, failed_metadata_path
                )  # Copy metadata if exists
            continue

        (_, ext) = os.path.splitext(image_path)

        if not ext[1:].casefold() in piexifCodecs:
            print(
                CURSOR_UP_FACTORY(2),
                "'Photo format is not supported:':",
                image_path,
                CLR,
                CURSOR_DOWN_FACTORY(2),
            )

            errorCounter += 1
            # Copy the image and metadata to the corresponding failed sub-folder
            failed_image_path = os.path.join(
                failed_folder, os.path.relpath(image_path, root_folder)
            )
            failed_metadata_path = os.path.join(
                failed_folder, os.path.relpath(metadata_path, root_folder)
            )
            dir = os.path.dirname(failed_image_path)
            if not os.path.exists(dir):
                os.makedirs(dir)  # Create subfolder

            shutil.copy2(image_path, dir)  # Copy image to failed folder
            if os.path.exists(metadata_path):
                shutil.copy2(metadata_path, dir)  # Copy metadata if exists
            continue

        image = Image.open(image_path, mode="r").convert("RGB")
        image_exif = image.getexif()
        if OrientationTagID in image_exif:
            orientation = image_exif[OrientationTagID]

            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)

        if max_dimension:
            image.thumbnail(max_dimension)

        new_image_path = get_output_filename(root_folder, out_folder, image_path)

        dir = os.path.dirname(new_image_path)

        if not os.path.exists(dir):
            os.makedirs(dir)

            # Handle missing metadata gracefully
        if not os.path.exists(metadata_path):
            # Copy the image and metadata to the corresponding failed sub-folder
            failed_image_path = os.path.join(
                failed_folder, os.path.relpath(os.path.dirname(image_path), root_folder)
            )
            dir = os.path.dirname(failed_image_path)
            if not os.path.exists(dir):
                os.makedirs(dir)  # Create subfolder
            shutil.copy2(image_path, failed_image_path)
            print(f"No metadata for {image_path}.")
            errorCounter += 1
            continue

        try:
            with open(metadata_path, encoding="utf8") as f:
                metadata = json.load(f)

            timeStamp = int(metadata["photoTakenTime"]["timestamp"])
            # If the metadata exists, use it to adjust EXIF and save
            if "exif" in image.info:
                new_exif = adjust_exif(image.info["exif"], metadata)
                image.save(new_image_path, quality=optimize, exif=new_exif)
            else:
                image.save(new_image_path, quality=optimize)
        except Exception as e:
            print(f"Error loading metadata for {image_path}: {e}. Moved to failed.")
            # If there's an issue with the metadata, copy to the failed folder
            failed_image_path = os.path.join(
                failed_folder, os.path.relpath(os.path.dirname(image_path), root_folder)
            )
            shutil.copy2(image_path, failed_image_path)
            errorCounter += 1
            continue

        setFileCreationTime(new_image_path, timeStamp)

        successCounter += 1

    print()
    print("Metadata merging has been finished")
    print("Success", successCounter)
    print("Failed", errorCounter)
