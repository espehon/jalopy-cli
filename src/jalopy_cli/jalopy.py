# Copyright (c) 2024, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html


import os
import sys
import argparse
import json
import importlib.metadata
from configparser import ConfigParser


import pandas as pd
# import copykitten
import questionary

# Set file paths
storage_folder = os.path.expanduser("~/.share/jalopy/")
storage_file = "jalopy.csv"
storage_path = storage_folder + storage_file

# Check if storage folder exists, create it if missing.
if os.path.exists(os.path.expanduser(storage_folder)) == False:
    os.makedirs(storage_folder)

# Check if storage file exists, create it if missing.
if os.path.exists(storage_path) == False:
    headers = ['Date', 'Vehicle', 'Odometer', 'Units', 'Work', 'Cost', 'Note']
    df = pd.DataFrame(columns=headers)
    df.to_csv(storage_path, index=False)



# Set argument parsing
parser = argparse.ArgumentParser(
    description="Tasky: A to-do list program!\n\nBased off of klaudiosinani's Taskbook for JavaScript.",
    epilog="Examples: ts --task this is a new task, ts --switch 1, ts --complete 1",
    allow_abbrev=False,
    add_help=False,
    usage="ts [option] <arguments>    'try: ts --help'"
)

parser.add_argument('-?', '--help', action='help', help='Show this help message and exit.')
parser.add_argument('-t', '--task', action='store_true', help='Add a new task')
parser.add_argument('-c', '--complete', nargs='+', metavar='T', action='store', type=int, help='Mark task(s) complete')
parser.add_argument('-s', '--switch', nargs='+', metavar='T', action='store', type=int, help='Toggle task(s) as started/stopped')
parser.add_argument('-f', '--flag', nargs='+', metavar='T', action='store', type=int, help='Flag task(s) with astrict (*)')
parser.add_argument('-p', '--priority', nargs=2, metavar=('T', 'P'), action='store', type=int, help='Set the priority of task [T] to [P]')
parser.add_argument('-e', '--edit', nargs=1, metavar='T', action='store', type=int, help='Enter edit mode on a task')
parser.add_argument('-d', '--delete', nargs='+', metavar='T', action='store', type=int, help='Mark task [T] for deletion')
parser.add_argument('--clean', action='store_true', help='Remove complete/deleted tasks and reset indices')
parser.add_argument('text', nargs=argparse.REMAINDER, help='Task description that is used with --task')

config = ConfigParser()