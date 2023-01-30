## Migrate Google Photos to iCloud

1. Export photos in https://takeout.google.com/
2. Extra files into one folder
  
      If you have multiple .zip files you can extra with `ditto` in `macos`
        
        ditto -x -k *.zip ./takeout_photos

3. Clone this repo / Download the source code
       
   You can clone the source code if you have git in your system
       
       git clone https://github.com/Greegko/google-metadata-matcher
       
   Alternative, you can download the reposity source code, which is behind the green code button on the project.
       
5. install dependencies

       cd google-metadata-matcher
       pip3 install -r requirements.txt

4. Run the metadata merger on the images

       python3 src/merge_metadata.py <takeout_photos_id> <output_directory>
