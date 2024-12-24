# Copyright (c) 2024, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html


import os
import sys
import argparse
import json
import importlib.metadata
from configparser import ConfigParser
from datetime import datetime, timedelta


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
    df = pd.DataFrame(columns=['Key', 'Date', 'Vehicle', 'Odometer', 'Units', 'Service', 'Cost', 'Note'])
    df.to_csv(storage_path, index=False)

data = pd.read_csv(storage_path)



# Set argument parsing
parser = argparse.ArgumentParser(
    description="Jalopy! Log vehicle maintenance via the commandline! Enter 'jalopy' with no arguments to start entry.",
    epilog="Jalopy (Noun): An old vehicle. Can be used as an insult or a term of endearment :)",
    allow_abbrev=False,
    add_help=False,
    usage="jalopy [option] <arguments>    'try: jalopy --help'"
)

parser.add_argument('-?', '--help', action='help', help='Show this help message and exit.')
parser.add_argument('-h', '--history', nargs='?', metavar='N', const=10, action='store', type=int, help='Show the last [N] entries. Default 10')

# parser.add_argument('-t', '--task', action='store_true', help='Add a new task')
# parser.add_argument('-c', '--complete', nargs='+', metavar='T', action='store', type=int, help='Mark task(s) complete')
# parser.add_argument('-s', '--switch', nargs='+', metavar='T', action='store', type=int, help='Toggle task(s) as started/stopped')
# parser.add_argument('-f', '--flag', nargs='+', metavar='T', action='store', type=int, help='Flag task(s) with astrict (*)')
# parser.add_argument('-p', '--priority', nargs=2, metavar=('T', 'P'), action='store', type=int, help='Set the priority of task [T] to [P]')
# parser.add_argument('-e', '--edit', nargs=1, metavar='T', action='store', type=int, help='Enter edit mode on a task')
# parser.add_argument('--clean', action='store_true', help='Remove complete/deleted tasks and reset indices')
# parser.add_argument('text', nargs=argparse.REMAINDER, help='Task description that is used with --task')

config = ConfigParser()


def new_entry():
    key = get_next_key(data)
    date = get_date()
    vehicle = get_vehicle(data)
    units = get_units(data, vehicle)
    odometer = get_odometer(units)
    # ask for service
    # ask for cost
    # ask for optional note
    # check for custom headers and ask for values

    # add the entry to the dataframe
    pass


def get_next_key(df) -> int:
    # get the next key for the dataframe; will be max + 1
    if df.empty:
        return 1
    else:
        return df['Key'].max() + 1


def get_date() -> str:
    # Generate a list of dates from today to the last 7 days
    today = datetime.today()
    date_options = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(8)]
    date_options.append('Custom')
    
    # Prompt the user to select a date
    selected_date = questionary.select( "Select a date:", choices=date_options ).ask()

    # If 'Custom' is selected, prompt the user to enter a date manually 
    if selected_date == 'Custom':
        tries = 3
        while tries > 0:
            selected_date = questionary.text("Enter a date (YYYY-MM-DD):").ask()
            try:
                # Validate the custom date format
                datetime.strptime(selected_date, '%Y-%m-%d')
                break
            except ValueError:
                print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
                tries -= 1
                if tries == 0:
                    print("Too many invalid attempts. Using today's date.")
                    selected_date = date_options[0]

    return selected_date


def get_vehicle(df):
    # Get the list of vehicles from the DataFrame 
    vehicles = df['Vehicle'].unique().tolist()
    vehicles.append('New') 

    # Prompt the user to select a vehicle
    selected_vehicle = questionary.select( "Select a vehicle:", choices=vehicles ).ask()

    # If 'New' is selected, prompt the user to enter a new vehicle
    if selected_vehicle == 'New':
        selected_vehicle = questionary.text("Enter a new vehicle:").ask()

    return selected_vehicle


def get_units(df, vehicle):
    # Function to get the units
    # Filter the DataFrame for the given vehicle
    vehicle_df = df[df['Vehicle'] == vehicle]
    # Check if there are any units for the given vehicle
    if not vehicle_df.empty:
        units = vehicle_df['Units'].iloc[0]
    else:
        # Prompt the user to select Miles or Km 
        units = questionary.select( "Select units:", choices=['Miles', 'Km'] ).ask()
    return units


def get_odometer(units):
    # Prompt the user for the odometer value with units in the prompt
    odometer_value = questionary.text(f"Enter the odometer value ({units}):").ask()
    return odometer_value




def jalopy(argv=None):
    args = parser.parse_args(argv)

    if args.history:
        print("print history not yet added.")
    
    else:
        print("add entry not yet ready")
    
    print(args)

