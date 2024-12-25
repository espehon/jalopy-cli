# Copyright (c) 2024, espehon
# License: https://www.gnu.org/licenses/gpl-3.0.html

import os
import sys
import argparse
import json
import importlib.metadata
from configparser import ConfigParser
from datetime import datetime, timedelta
from collections import Counter


import pandas as pd
import questionary

# Get version of this package
try:
    __version__ = f"jalopy {importlib.metadata.version('jalopy_cli')} from jalopy_cli"
except importlib.metadata.PackageNotFoundError:
    __version__ = "Package not installed..."

# Set file paths
config_path = os.path.expanduser('~/.config/jalopy/jalopy.json')
config_path = config_path.replace('\\', '/')
if os.path.exists(config_path):
    with open(config_path, 'r') as file:
        settings = json.load(file)
else:
    settings = {'storage_path': '~/.local/share/jalopy/'}
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as file:
        json.dump(settings, file, indent=4)

storage_folder = os.path.expanduser(settings['storage_path'])
storage_folder = storage_folder.replace('\\', '/')
storage_file = "jalopy.csv"
storage_path = storage_folder + storage_file

# Check if storage folder exists, create it if missing.
if os.path.exists(os.path.expanduser(storage_folder)) == False:
    os.makedirs(storage_folder)

# Check if storage file exists, create it if missing.
if os.path.exists(storage_path) == False:
    starter_df = pd.DataFrame(columns=['Key', 'Date', 'Vehicle', 'Odometer', 'Units', 'Service', 'Cost', 'Note'])
    starter_df.to_csv(storage_path, index=False)

data = pd.read_csv(storage_path)

# Predefined list of common services with their frequencies
common_services = {
    'Oil': 10,
    'Engine Air Filter': 9,
    'Cabin Air Filter': 8,
    'Brakes': 7,
    'Battery Check': 6,
    'Registration': 5,
    'Tire Rotation': 4,
    'New Tires': 3,
    'Spark Plugs': 2,
    'Transmission Fluid': 1
}

# Set argument parsing
parser = argparse.ArgumentParser(
    description="Jalopy! Log vehicle maintenance via the commandline!",
    epilog="Jalopy (Noun): An old vehicle. Can be used as an insult or a term of endearment :)",
    allow_abbrev=False,
    add_help=False,
    usage="jalopy [option] <arguments>    # Enter 'jalopy' with no arguments to start entry."
)

parser.add_argument('-?', '--help', action='help', help='Show this help message and exit.')
parser.add_argument('-v', '--version', action='version', version=__version__, help="Show package version and exit.")
parser.add_argument('-h', '--history', nargs='*', metavar='N', help='Show the last [N] entries for vehicle(s) [N]. N can be a number or a vehicle name. Vehicle names are case sensitive and multiple can be passed. Default is 10 entries for all vehicles.')

config = ConfigParser()


# Function to check if value is a valid number
def is_valid_number(number, minimum=sys.float_info.min, maximum=sys.float_info.max):
    try:
        if float(number) >= minimum and float(number) <= maximum:
            return True
        else:
            raise ValueError
    except ValueError:
        return False


# Function to generate a series of prompts for a new entry
def new_entry():
    key = get_next_key(data)
    date = get_date()
    vehicle = get_vehicle(data)
    units = get_units(data, vehicle)
    odometer = get_odometer(units)
    service = get_service(data, vehicle)
    cost = get_cost()
    note = get_note()
    return key, date, vehicle, units, odometer, service, cost, note


# Function to get the next key for the dataframe; will be max + 1
def get_next_key(df) -> int:
    if df.empty:
        return 1
    else:
        return df['Key'].max() + 1


# Function to select a date
def get_date() -> str:
    # Generate a list of dates from today to the last 7 days
    today = datetime.today()
    date_options = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(8)]
    date_options.append('Custom')
    
    # Prompt the user to select a date
    selected_date = questionary.select( "Select a date:", choices=date_options ).unsafe_ask()

    # If 'Custom' is selected, prompt the user to enter a date manually 
    if selected_date == 'Custom':
        tries = 3
        while tries > 0:
            selected_date = questionary.text("Enter a date (YYYY-MM-DD):").unsafe_ask()
            try:
                # Validate the custom date format
                datetime.strptime(selected_date, '%Y-%m-%d')
                return selected_date
            except ValueError:
                print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
                tries -= 1
                if tries == 0:
                    print("Too many invalid attempts. Using today's date.")
                    selected_date = date_options[0]
    else:
        return selected_date


# Function to get the vehicle
def get_vehicle(df):
    # Get the list of vehicles from the DataFrame 
    vehicles = df['Vehicle'].unique().tolist()
    vehicles.append('New') 

    # Prompt the user to select a vehicle
    selected_vehicle = questionary.select( "Select a vehicle:", choices=vehicles ).unsafe_ask()

    # If 'New' is selected, prompt the user to enter a new vehicle
    if selected_vehicle == 'New':
        tries = 3
        while tries > 0:
            selected_vehicle = questionary.text("Enter a new vehicle:").unsafe_ask().strip()
            if len(selected_vehicle) > 0:
                return selected_vehicle
            else:
                print("Invalid input. Please enter at least one character.")
                tries -= 1
                if tries == 0:
                    print("Too many invalid attempts. Exiting...")
                    sys.exit(1)
    return selected_vehicle


# Function to get the units
def get_units(df, vehicle):
    # Filter the DataFrame for the given vehicle
    vehicle_df = df[df['Vehicle'] == vehicle]
    # Check if there are any units for the given vehicle
    if not vehicle_df.empty:
        units = vehicle_df['Units'].iloc[0]
    else:
        # Prompt the user to select Miles or Km 
        units = questionary.select( "Select units:", choices=['Miles', 'Km'] ).unsafe_ask()
    return units


# Function to get the odometer value
def get_odometer(units):
    # Prompt the user for the odometer value with units in the prompt
    tries = 3
    while tries > 0:
        odometer_value_input = questionary.text(f"Enter the odometer value ({units}):").unsafe_ask()
        try:
            # Validate the cost input 
            odometer_value = int(odometer_value_input)
            if is_valid_number(odometer_value, 0):
                return odometer_value
            raise ValueError
        except ValueError:
            print("Invalid input. Please enter a valid whole number.")
            tries -= 1
            if tries == 0:
                print("Too many invalid attempts. Exiting...")
                sys.exit(1)

# Function to get the service
def get_service(df, vehicle):
    # Filter the DataFrame for the given vehicle
    vehicle_df = df[df['Vehicle'] == vehicle].dropna(subset=['Service'])

    # Get the list of services for the given vehicle
    vehicle_services = vehicle_df['Service'].tolist()

    # Combine the common services with the vehicle services
    combined_services = Counter(common_services) + Counter(vehicle_services)

    # Create a sorted list of services based on frequency 
    sorted_services = [service for service, _ in combined_services.most_common()]

    # Add the 'None' and 'New' options at the end
    sorted_services.append('None')
    sorted_services.append('New')

    # Prompt the user to select a service
    selected_service = questionary.select( "Select a service:", choices=sorted_services ).unsafe_ask()

    # If 'New' is selected, prompt the user to enter a new service
    if selected_service == 'New':
        selected_service = questionary.text("Enter a new service:").unsafe_ask().strip()

    return selected_service


# Function to get the cost
def get_cost():
    tries = 3
    while tries > 0:
        cost_input = questionary.text("Enter the cost:").unsafe_ask().strip()
        try:
            # Validate the cost input 
            if is_valid_number(cost_input, 0):
                return cost_input
            raise ValueError
        except ValueError:
            print("Invalid input. Please enter a valid float number.")
            tries -= 1
            if tries == 0:
                print("Too many invalid attempts. Exiting...")
                sys.exit(1)


# Function to get the note
def get_note():
    note = questionary.text("Enter a note:").unsafe_ask().strip()
    return note


# Function to add a new entry to the DataFrame
def add_new_entry(data, key, date, vehicle, units, odometer, service, cost, note):
    new_row = {
        'Key': key,
        'Date': date,
        'Vehicle': vehicle,
        'Odometer': odometer,
        'Units': units,
        'Service': service,
        'Cost': cost,
        'Note': note
    }
    data.loc[len(data)] = new_row
    return data


# Function to print the last N rows of the DataFrame and filter by vehicle
def print_history(data, passed_args):
    n = None
    v = []

    for arg in passed_args:
        if n == None and is_valid_number(arg, 1):
            n = int(arg)
        else:
            v.append(arg)
    if n == None:
        n = 10
    if v:
        data = data[data['Vehicle'].isin(v)]
    # Get the last N rows
    history = data.tail(n)
    # Print the history neatly
    print(history.to_string(index=False))


# Main function
def jalopy(data=data, argv=None):
    args = parser.parse_args(argv)
    print(args)

    if args.history != None:
        print_history(data, args.history)
    
    else:
        try:
            # Get new entry values
            key, date, vehicle, units, odometer, service, cost, note = new_entry()
            # Add the new entry to the DataFrame
            data = add_new_entry(data, key, date, vehicle, units, odometer, service, cost, note)
            # Write changes to storage
            data.to_csv(storage_path, index=False)
            questionary.print(f"✔  Entry added to {storage_path}", style="italic darkgreen")
        except KeyboardInterrupt:
            print("KeyboardInterrupt detected, aborting...")
    
    