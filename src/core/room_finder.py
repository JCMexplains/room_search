import glob
import logging
import os
from copy import deepcopy
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import pandas as pd

# Get project root directory (assuming src is a subdirectory of the project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Create logs directory if it doesn't exist
os.makedirs(PROJECT_ROOT / "logs", exist_ok=True)

# Set up logging with absolute path
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(PROJECT_ROOT / "logs/room_finder.log")),
        logging.StreamHandler(),
    ],
)

from src.core.constants.my_rooms import MY_ROOMS
from src.core.constants.room_caps import get_room_cap
from src.core.constants.time_blocks import TIME_BLOCKS


def parse_time(time_str: str) -> datetime:
    """Convert time string to datetime object"""
    try:
        if isinstance(time_str, str):
            return datetime.strptime(time_str.strip(), "%H:%M")
        return time_str  # Return as is if already a datetime
    except ValueError as e:
        logging.error(f"Failed to parse time '{time_str}': {e}")
        return None


def parse_date(date_str: str) -> Optional[date]:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        logging.error(f"Failed to parse date '{date_str}': {e}")
        return None


def do_dates_overlap(start1: date, end1: date, start2: date, end2: date) -> bool:
    return (start1 <= end2) and (end1 >= start2)


def is_conflict(class_time: Tuple[time, time], block_time: Tuple[time, time]) -> bool:
    """
    Check if two time blocks overlap.

    Args:
        class_time: Tuple of (start_time, end_time) for the class
        block_time: Tuple of (start_time, end_time) for the time block

    Returns:
        bool: True if the times overlap, False otherwise
    """
    class_start, class_end = class_time
    block_start, block_end = block_time

    return (class_start < block_end) and (block_start < class_end)


def find_vacant_rooms(
    term: int, days: List[str], data_file: str = "*data*.csv"
) -> Dict[str, Dict]:

    try:
        # At the very start, verify TIME_BLOCKS
        print("TIME_BLOCKS type:", type(TIME_BLOCKS))
        print("TIME_BLOCKS sample:", list(TIME_BLOCKS)[:2])

        # Define column name mappings (original -> standardized)
        COLUMN_MAPPING = {
            "Term": "term",
            "Building": "building",
            "Room Number": "room_number",  # Adjust if different in your CSV
            "Room Cap": "room_cap",  # Adjust if different in your CSV
            "Start Time": "start_time",  # Adjust if different in your CSV
            "End Time": "end_time",  # Adjust if different in your CSV
            "Days": "days",
        }

        print(f"Received days parameter: {days} (type: {type(days)})")

        # Find the most recent data file
        data_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "*data*.csv"
        )
        data_files = glob.glob(data_path)
        if not data_files:
            print(f"Searching for data files in: {data_path}")
            raise FileNotFoundError(f"No data files found matching {data_path}")
        latest_file = max(data_files, key=os.path.getctime)
        logging.info(f"Loading data from: {latest_file}")

        # Read CSV with explicit dtypes, but read building as string first
        df = pd.read_csv(
            latest_file,
            dtype={
                "building": str,  # Read as string first to handle 'TBA'
                "room_number": float,
                "room_cap": "Int64",  # Use nullable integer type
                "days": str,
                "term": "Int64",
            },
        )

        # Filter out rows where building is 'TBA' or non-numeric
        df = df[df["building"].str.isnumeric().fillna(False)]
        # Now convert building to int
        df["building"] = df["building"].astype(int)

        # Filter data for the requested term
        filtered_df = df[df["term"] == term]
        print(f"Found {len(filtered_df)} rows after filtering")

        # Print sample of filtered data
        print("\nSample of filtered data:")
        print(
            filtered_df[
                [
                    "building",
                    "room_number",
                    "room_cap",
                    "start_time",
                    "end_time",
                    "days",
                ]
            ].head()
        )
        print("\nSample of days column after filtering:")
        print(filtered_df["days"].head())
        print("Days column type:", filtered_df["days"].dtype)

        # Create a set of occupied time slots for each room
        occupied_slots = {}
        for _, row in filtered_df.iterrows():
            try:
                building = int(row["building"])
                room = (
                    int(float(row["room_number"]))
                    if pd.notna(row["room_number"])
                    else None
                )
                start = str(row["start_time"])
                end = str(row["end_time"])
                days_raw = row["days"]

                # Skip if we don't have valid building and room
                if room is None or pd.isna(building):
                    continue

                room_key = f"{building}-{room}"

                # Skip invalid time entries
                if pd.isna(start) or pd.isna(end):
                    continue

                if room_key not in occupied_slots:
                    occupied_slots[room_key] = {d: [] for d in "MTWRFS"}

                # Handle combined day codes (e.g., 'TR' -> ['T', 'R'])
                if pd.notna(days_raw):
                    # Convert to string and handle any numeric values
                    days_str = str(days_raw)
                    if days_str.isdigit():
                        print(f"Warning: Numeric day value found: {days_str}")
                        continue

                    # Convert day codes like 'TR' into individual days
                    day_chars = [c for c in days_str if c in "MTWRFS"]
                    for day in day_chars:
                        if (start, end) not in occupied_slots[room_key][day]:
                            occupied_slots[room_key][day].append((start, end))

            except Exception as e:
                print(f"Error processing row: {e}")
                print(f"Row data: days={days_raw}, building={building}, room={room}")
                continue

        print("\nOccupied slots sample:")
        # Print first few entries of occupied_slots
        for key in list(occupied_slots.keys())[:3]:
            print(f"{key}: {occupied_slots[key]}")

        # Now create the vacant rooms dictionary
        vacant_rooms = {}
        print("\nProcessing MY_ROOMS:", MY_ROOMS)  # Debug print

        for building, room in MY_ROOMS:
            try:
                room_key = f"{building}-{room}"
                print(f"\nProcessing room {room_key}")  # Debug print

                # Get room capacity from constants
                room_cap = get_room_cap(building, room)

                vacant_times = {}
                # Process each requested day
                for day in days:
                    print(f"  Checking day {day}")  # Debug print
                    vacant_times[day] = []  # Initialize empty list for this day

                    if room_key not in occupied_slots:
                        # Room has no occupancy data, all times are vacant
                        print(
                            f"    No occupancy data for {room_key} - marking all times vacant"
                        )
                        vacant_times[day] = list(TIME_BLOCKS)
                    else:
                        # Get occupied times for this day
                        occupied = occupied_slots[room_key].get(day, [])
                        print(f"    Found {len(occupied)} occupied times")

                        # Check each time block
                        for time_block in TIME_BLOCKS:
                            is_vacant = True
                            for occ_start, occ_end in occupied:
                                if overlaps(
                                    time_block[0], time_block[1], occ_start, occ_end
                                ):
                                    is_vacant = False
                                    break
                            if is_vacant:
                                vacant_times[day].append(time_block)

                # Always include the room, even if it has no vacant times
                vacant_rooms[room_key] = {
                    "capacity": room_cap,
                    "vacant_times": vacant_times,
                }

            except Exception as e:
                print(f"Error processing room {building}-{room}: {e}")
                continue

        print(f"\nFound {len(vacant_rooms)} rooms with vacant times")
        # Debug print a sample of the vacant_rooms structure
        if vacant_rooms:
            sample_key = next(iter(vacant_rooms))
            print(f"Sample vacant room data structure:")
            print(f"Key: {sample_key}")
            print(f"Value: {vacant_rooms[sample_key]}")

        # Ensure consistent data structure for all rooms
        final_rooms = {}
        for room_key, room_data in vacant_rooms.items():
            # Ensure each room has both capacity and vacant_times
            final_room = {
                "capacity": int(room_data.get("capacity", 0)),
                "vacant_times": {},
            }

            # Ensure each day has a list of time tuples
            for day in days:
                final_room["vacant_times"][day] = [
                    (str(start), str(end))
                    for start, end in room_data["vacant_times"].get(day, [])
                ]

            final_rooms[str(room_key)] = final_room

        print("\nFinal data structure verification:")
        print(f"Number of rooms: {len(final_rooms)}")
        if final_rooms:
            sample_key = next(iter(final_rooms))
            print(f"Sample final room: {sample_key}: {final_rooms[sample_key]}")

        # Before returning, verify all time blocks are tuples
        for room_data in final_rooms.values():
            for day_times in room_data["vacant_times"].values():
                for i, time_block in enumerate(day_times):
                    if not isinstance(time_block, tuple):
                        day_times[i] = tuple(time_block)

        # Before returning, add one final verification
        print("\nFinal verification before return:")
        print(f"Type of return value: {type(final_rooms)}")
        print(f"Keys in return value: {list(final_rooms.keys())}")
        print(f"Sample value type: {type(final_rooms[next(iter(final_rooms))])}")

        # Store the return value first
        result = final_rooms

        # Verify it's still a dictionary
        assert isinstance(result, dict), "Result is not a dictionary!"
        assert all(
            isinstance(v, dict) for v in result.values()
        ), "Not all values are dictionaries!"

        print("Final verification passed - returning dictionary")
        return result

    except Exception as e:
        print(f"Error in find_vacant_rooms: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error location: {e.__traceback__.tb_frame.f_code.co_name}")
        import traceback

        traceback.print_exc()
        raise


def overlaps(start1: str, end1: str, start2: str, end2: str) -> bool:
    """Check if two time ranges overlap"""
    try:
        s1 = parse_time(start1)
        e1 = parse_time(end1)
        s2 = parse_time(start2)
        e2 = parse_time(end2)

        if None in (s1, e1, s2, e2):
            print(f"Warning: Could not parse times: {start1}-{end1} vs {start2}-{end2}")
            return True  # Assume overlap if we can't parse times

        return (s1 <= e2) and (e1 >= s2)
    except Exception as e:
        print(f"Error comparing times: {start1}-{end1} with {start2}-{end2}: {e}")
        return True  # Assume overlap on error


def get_formatted_blocks(blocks, all_blocks):
    """Convert time blocks to formatted strings, with blanks for occupied times"""
    formatted = []

    # Convert blocks to comparable format
    blocks_set = {
        (parse_time(start).time(), parse_time(end).time()) for start, end in blocks
    }

    for block in all_blocks:
        if any(is_conflict(block, class_block) for class_block in blocks_set):
            # Room is vacant - show the time
            formatted.append(
                f"{block[0].strftime('%H:%M')}-{block[1].strftime('%H:%M')}"
            )
        else:
            # Room is occupied - show blank space
            formatted.append(" " * 11)  # Same width as "HH:MM-HH:MM"
        formatted.append("   ")  # Add 3 spaces of padding between blocks

    # Remove the trailing padding from the last block
    if formatted:
        formatted.pop()

    return formatted


def print_vacancies(
    vacancies: Dict[Tuple[int, int], Dict[str, List[Tuple[time, time]]]]
):
    # Get all possible time blocks from constants
    all_blocks = [(parse_time(start), parse_time(end)) for start, end in TIME_BLOCKS]

    # Print header with time blocks
    header_times = [
        f"{block[0].strftime('%H:%M')}-{block[1].strftime('%H:%M')}"
        for block in all_blocks
    ]
    print("\nTime slots:", "  ".join(header_times))
    print("-" * (len(header_times) * 13 + 20))  # Separator line

    for room, days in vacancies.items():
        print(f"\nBuilding {room[0]}, Room {room[1]}:")
        for day, blocks in days.items():
            formatted_blocks = get_formatted_blocks(blocks, all_blocks)
            print(f"{day:<3}: {' '.join(formatted_blocks)}")
