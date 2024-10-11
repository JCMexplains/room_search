import os
from datetime import datetime, time
from typing import List, Tuple
import tkinter as tk  # Add this import

import pandas as pd

from constants.my_rooms import MY_ROOMS
from constants.time_blocks import fall_spring_blocks as fall_spring_blocks_str
from constants.time_blocks import summer_blocks as summer_blocks_str


def convert_to_time_tuples(blocks: List[Tuple[str, str]]) -> List[Tuple[time, time]]:
    return [
        (
            datetime.strptime(start, "%H:%M").time(),
            datetime.strptime(end, "%H:%M").time(),
        )
        for start, end in blocks
    ]


# Convert the imported blocks to datetime.time objects
fall_spring_blocks = convert_to_time_tuples(fall_spring_blocks_str)
summer_blocks = convert_to_time_tuples(summer_blocks_str)


def is_summer(term):
    return str(term).endswith("3")


def class_in_block(class_start, class_end, block_start, block_end):
    # print(
    #     f"Debug: class_start type: {type(class_start)}, class_end type: {type(class_end)}"
    # )
    start_in_block = block_start <= class_start < block_end
    end_in_block = block_start < class_end <= block_end
    spans_block = class_start <= block_start and class_end >= block_end
    return start_in_block or end_in_block or spans_block


def expand_days(days_string):
    return pd.Series(
        {
            day: day in days_string if pd.notna(days_string) else False
            for day in "MTWRFS"
        }
    )


def parse_time(time_str):
    if pd.isna(time_str):
        return None
    time_str = time_str.strip()
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        print(f"Warning: Unable to parse time '{time_str}'. Returning None.")
        return None


def find_unoccupied_rooms(selected_days=None, selected_rooms=None):
    # Define column types
    dtypes = {
        "building": int,
        "campus": str,
        "course_id": str,
        "days": str,
        "delivery_method": str,
        "department": str,
        "division": str,
        "end_date": str,
        "instructor_name": str,
        "reference_number": int,
        "room_number": int,
        "session": int,
        "start_date": str,
        "start_time": str,
        "end_time": str,
        "term": int,
    }

    # Add room_cap to the dtypes dictionary
    dtypes["room_cap"] = int

    # Read CSV file
    df = pd.read_csv(
        os.path.join("data", "data.csv"),
        dtype=dtypes,
        skipinitialspace=True,
    )

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Apply parse_time function to start_time and end_time columns
    df["start_time"] = df["start_time"].apply(parse_time)
    df["end_time"] = df["end_time"].apply(parse_time)

    # Expand the 'days' column
    day_columns = df["days"].apply(expand_days)
    df = pd.concat([df.drop("days", axis=1), day_columns], axis=1)

    # Use selected options or default to all if not provided
    selected_days = selected_days or list("MTWRFS")
    selected_rooms = selected_rooms or MY_ROOMS

    # Initialize occupancy dictionary
    occupancy = {
        (building, room): {day: set() for day in selected_days}
        for building, room in selected_rooms
    }

    # Create a dictionary to store room capacities
    room_capacities = {}

    # Fill occupancy dictionary and room capacities
    for _, row in df.iterrows():
        building = row["building"]
        room = row["room_number"] if pd.notna(row["room_number"]) else None
        if (building, room) in selected_rooms:
            # Store room capacity
            room_capacities[(building, room)] = row["room_cap"]

            blocks = summer_blocks if is_summer(row["term"]) else fall_spring_blocks

            if row["start_time"] is not None and row["end_time"] is not None:
                for block_start, block_end in blocks:
                    if class_in_block(
                        row["start_time"], row["end_time"], block_start, block_end
                    ):
                        for day in selected_days:
                            if row[day]:
                                occupancy[(building, room)][day].add(
                                    (block_start, block_end)
                                )

    # Find and return unoccupied time slots
    unoccupied_slots = {}
    for (building, room), days in occupancy.items():
        unoccupied_slots[(building, room)] = {}
        for day, occupied_blocks in days.items():
            unoccupied_slots[(building, room)][day] = set(blocks) - occupied_blocks

    # print("Room capacities:", room_capacities)  # Debug print

    return unoccupied_slots, room_capacities


def run_room_search():
    unoccupied_slots, room_capacities = find_unoccupied_rooms()
    
    # Import the GUI class here to avoid circular imports
    from rs_gui import RoomSearchGUI
    
    # Create and run the GUI
    root = tk.Tk()
    gui = RoomSearchGUI(root, unoccupied_slots, room_capacities)
    root.mainloop()

if __name__ == "__main__":
    run_room_search()
