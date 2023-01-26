import os
import sys
from process_folder import processFolder
import argparse

def dimension(s):
    try:
        width, height = map(int, s.split(','))
        return (width, height)
    except:
        raise argparse.ArgumentTypeError("Dimension must be width,height")

parser = argparse.ArgumentParser()

parser.add_argument('source_folder')
parser.add_argument('output_folder')
parser.add_argument('-w',  '--edited_word', default='edited')
parser.add_argument('-o',  '--optimize', type=int, default=100)
parser.add_argument('-m',  '--max_dimension', type=dimension)

args = parser.parse_args()

if not os.path.exists(args.source_folder):
  print('Target folder doesn\'t exist')
  exit()

processFolder(args.source_folder, args.edited_word, args.optimize, args.output_folder, args.max_dimension)
