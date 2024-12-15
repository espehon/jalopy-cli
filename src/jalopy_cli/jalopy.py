# Copyright (c) 2024, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html


import os
import sys
import argparse
import json
import importlib.metadata

import pandas as pd
import copykitten
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
    
