## Migrate Google Photos to iCloud

1. Export photos in https://takeout.google.com/
2. Extra files into one folder
  
      If you have multiple .zip files you can extra with `ditto` in `macos`
        
        ditto -x -k *.zip ./takeout_photos

3. Clone this repo and install dependencies

       clone <TODO:gitsource> <target_dir>
       cd <target_dir>
       pip3 install -r requirements.txt

4. Run the metadata merger on the images

       python3 src/merge_metadata.py <takeout_photos_id> <output_directory>