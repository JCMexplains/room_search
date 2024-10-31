import os
from datetime import datetime, time
from typing import List, Tuple, Dict, Set, Optional
import tkinter as tk 

import pandas as pd

from constants.col_types import dtypes
from constants.my_rooms import MY_ROOMS
from constants.time_blocks import fall_spring_blocks as fall_spring_blocks_str
from constants.time_blocks import summer_blocks as summer_blocks_str
from constants.term_session_dates import TERM_SESSION_DATES, get_dates


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


def is_summer(term: int) -> bool:
    return str(term).endswith("3")


def class_in_block(class_start: time, class_end: time, block_start: time, block_end: time) -> bool:
    start_in_block = block_start <= class_start < block_end
    end_in_block = block_start < class_end <= block_end
    spans_block = class_start <= block_start and class_end >= block_end
    return start_in_block or end_in_block or spans_block


def expand_days(days_string: Optional[str]) -> pd.Series:
    return pd.Series(
        {
            day: day in days_string if pd.notna(days_string) else False
            for day in "MTWRFS"
        }
    )


def parse_time(time_str: Optional[str]) -> Optional[time]:
    if pd.isna(time_str):
        return None
    time_str = time_str.strip()
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        print(f"Warning: Unable to parse time '{time_str}'. Returning None.")
        return None


def find_unoccupied_rooms(
    selected_days: Optional[List[str]] = None,
    selected_rooms: Optional[List[Tuple[int, int]]] = None,
    selected_time_slots: Optional[List[Tuple[time, time]]] = None,
    selected_term: Optional[int] = None,
    selected_session: Optional[int] = None
) -> Tuple[Dict[Tuple[int, int], Dict[str, Set[Tuple[time, time]]]], Dict[Tuple[int, int], int], List[Tuple[time, time]]]:
    """
    Find unoccupied rooms based on selected criteria.

    This function processes a CSV file containing room occupancy data and returns
    information about unoccupied rooms, room capacities, and available time slots.

    Args:
        selected_days (Optional[List[str]]): List of days to consider (e.g., ["M", "W", "F"]).
            If None, all days are considered.
        selected_rooms (Optional[List[Tuple[int, int]]]): List of (building, room) tuples to consider.
            If None, all rooms are considered.
        selected_time_slots (Optional[List[Tuple[time, time]]]): List of time slots to consider.
            If None, all time slots for the relevant semester are considered.
        selected_term (Optional[int]): List of terms to consider.
            If None, all terms are considered.
        selected_session (Optional[int]): List of sessions to consider.
            If None, all sessions are considered.

    Returns:
        Tuple[Dict[Tuple[int, int], Dict[str, Set[Tuple[time, time]]]], Dict[Tuple[int, int], int], List[Tuple[time, time]]]:
            - A dictionary of unoccupied time slots for each room and day.
            - A dictionary of room capacities.
            - A list of all time slots considered for the relevant semester.

    Note:
        This function reads data from a CSV file named 'data.csv' in the 'data' directory.
        It determines the semester (fall/spring or summer) based on the term data in the CSV.
    """

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

    # Filter by selected terms if provided
    if selected_term:
        df = df[df['term'] == selected_term]

    # Determine the semester based on the data
    terms = df['term'].unique()
    is_summer_term = any(is_summer(term) for term in terms)
    semester_blocks = summer_blocks if is_summer_term else fall_spring_blocks

    # Use selected options or default to all if not provided
    selected_days = selected_days or list("MTWRFS")
    selected_rooms = selected_rooms or MY_ROOMS
    selected_time_slots = selected_time_slots or semester_blocks

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
            # Start with all selected time slots
            available_slots = set(selected_time_slots)
            # Remove occupied blocks
            available_slots -= occupied_blocks
            unoccupied_slots[(building, room)][day] = available_slots

    # print("Room capacities:", room_capacities)  # Debug print

    # Get date range for term and session if both are provided
    session_start = None
    session_end = None
    if selected_term and selected_session:
        session_start, session_end = get_dates(selected_term, selected_session)
        if session_start and session_end:
            session_start = pd.to_datetime(session_start)
            session_end = pd.to_datetime(session_end)
            # Filter df to only include rows that overlap with the session dates
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['end_date'] = pd.to_datetime(df['end_date'])
            df = df[
                (df['start_date'] <= session_end) & 
                (df['end_date'] >= session_start)
            ]

    return unoccupied_slots, room_capacities, semester_blocks


def run_room_search() -> None:
    # Initial call without term/session filtering
    unoccupied_slots, room_capacities, semester_blocks = find_unoccupied_rooms()
    
    # Import the GUI class here to avoid circular imports
    from rs_gui import RoomSearchGUI
    
    # Create and run the GUI
    root = tk.Tk()
    gui = RoomSearchGUI(root, unoccupied_slots, room_capacities, semester_blocks, MY_ROOMS)
    root.mainloop()

if __name__ == "__main__":
    run_room_search()
