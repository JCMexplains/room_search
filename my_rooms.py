import os
import pandas as pd

# Path to the CSV file
csv_path = os.path.join(os.path.dirname(__file__), 'data', 'data.csv')

# Read the CSV file
df = pd.read_csv(csv_path)

# Create MY_ROOMS list from the DataFrame
MY_ROOMS = df[['building', 'room_number', 'room_cap']].drop_duplicates().values.tolist()

def get_room_capacity(building, room):
    """
    Get the capacity of a given room in a building.

    :param building: The building number (integer)
    :param room: The room number (integer)
    :return: The room capacity (integer) or 'Unknown' if not found
    """
    for b, r, capacity in MY_ROOMS:
        if b == building and r == room:
            return capacity
    return 'Unknown'

def is_valid_room(building, room):
    """
    Check if a given building and room combination is in the MY_ROOMS list.

    :param building: The building number (integer)
    :param room: The room number (integer)
    :return: True if the combination is in MY_ROOMS, False otherwise
    """
    return any(b == building and r == room for b, r, _ in MY_ROOMS)
