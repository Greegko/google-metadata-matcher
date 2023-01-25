import os
import sys
from process_folder import processFolder

try: 
  path = sys.argv[1]

  if not os.path.exists(path):
    print('Target folder doesnt exist')
    exit()
except:
    print('Provide target folder!')
    exit()

out_folder = len(sys.argv) > 2 and sys.argv[2]
replace = bool(out_folder)

processFolder(path, 'edited', 75, replace, out_folder)