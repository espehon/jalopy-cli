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
# import copykitten
import questionary

# Set file paths
storage_folder = os.path.expanduser("~/.local/share/jalopy/")
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

# Function to get the vehicle
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


# Function to get the units
def get_units(df, vehicle):
    # Filter the DataFrame for the given vehicle
    vehicle_df = df[df['Vehicle'] == vehicle]
    # Check if there are any units for the given vehicle
    if not vehicle_df.empty:
        units = vehicle_df['Units'].iloc[0]
    else:
        # Prompt the user to select Miles or Km 
        units = questionary.select( "Select units:", choices=['Miles', 'Km'] ).ask()
    return units

# Function to get the odometer value
def get_odometer(units):
    # Prompt the user for the odometer value with units in the prompt
    odometer_value = questionary.text(f"Enter the odometer value ({units}):").ask()
    return odometer_value


# Function to get the service
def get_service(df, vehicle):
    # Filter the DataFrame for the given vehicle
    vehicle_df = df[df['Vehicle'] == vehicle]

    # Get the list of services for the given vehicle
    vehicle_services = vehicle_df['Service'].tolist()

    # Combine the common services with the vehicle services
    combined_services = Counter(common_services) + Counter(vehicle_services)

    # Create a sorted list of services based on frequency 
    sorted_services = [service for service, _ in combined_services.most_common()]

    # Add the 'New' option at the end
    sorted_services.append('New')

    # Prompt the user to select a service
    selected_service = questionary.select( "Select a service:", choices=sorted_services ).ask()

    # If 'New' is selected, prompt the user to enter a new service
    if selected_service == 'New':
        selected_service = questionary.text("Enter a new service:").ask()

    return selected_service


# Function to get the cost
def get_cost():
    tries = 3
    while tries > 0:
        cost_input = questionary.text("Enter the cost:").ask().strip()
        try:
            # Validate the cost input 
            cost = float(cost_input)
            return cost
        except ValueError:
            print("Invalid input. Please enter a valid float number.")
            tries -= 1
            if tries == 0:
                print("Too many invalid attempts. Exiting.")
                return None


# Function to get the note
def get_note():
    note = questionary.text("Enter a note:").ask().strip()
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


# Function to print the last N rows of the DataFrame
def print_history(data, n=10):
    # Get the last N rows
    history = data.tail(n)
    # Print the history neatly
    print(history.to_string(index=False))


def jalopy(data=data, argv=None):
    args = parser.parse_args(argv)

    if args.history:
        print_history(data, args.history)
    
    else:
        # Get new entry values
        key, date, vehicle, units, odometer, service, cost, note = new_entry()
        # Add the new entry to the DataFrame
        data = add_new_entry(data, key, date, vehicle, units, odometer, service, cost, note)
        # Write changes to storage
        data.to_csv(storage_path, index=False)
    
    print(args)

