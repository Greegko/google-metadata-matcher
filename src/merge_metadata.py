import os
import sys
from process_folder import processFolder
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('source_folder')
parser.add_argument('output_folder', nargs='?')
parser.add_argument('-w',  '--edited_word', default='edited')
parser.add_argument('-rm', '--remove_metadata', action='store_true')
parser.add_argument('-e',  '--edit_inline', action='store_true')
parser.add_argument('-o',  '--optimize', type=int, default=75)

args = parser.parse_args()

if not os.path.exists(args.source_folder):
  print('Target folder doesn\'t exist')
  exit()

if args.edit_inline and args.output_folder:
  print('Cannot edit inline and having an output folder')
  exit()

processFolder(args.source_folder, args.edited_word, args.optimize, args.remove_metadata, args.edit_inline, args.output_folder)
