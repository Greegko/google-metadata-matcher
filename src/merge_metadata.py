import os
import sys
from process_folder import processFolder
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('source_folder')
parser.add_argument('output_folder')
parser.add_argument('-w',  '--edited_word', default='edited')
parser.add_argument('-o',  '--optimize', type=int, default=75)

args = parser.parse_args()

if not os.path.exists(args.source_folder):
  print('Target folder doesn\'t exist')
  exit()

processFolder(args.source_folder, args.edited_word, args.optimize, args.output_folder)
