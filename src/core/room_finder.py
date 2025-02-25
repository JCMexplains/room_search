import logging
import os
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/room_finder.log"), logging.StreamHandler()],
)

from src.core.constants.my_rooms import MY_ROOMS
from src.core.constants.term_session_dates import get_dates
from src.core.constants.time_blocks import TIME_BLOCKS


def parse_time(time_str: str) -> Optional[time]:
    try:
        return datetime.strptime(time_str, "%H:%M").time()
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

    return (
        block_start <= class_start <= block_end
        or block_start <= class_end <= block_end
        or class_start <= block_start <= class_end
    )


def find_vacant_rooms(
    term: int, session: int, days: List[str], data_file: str = "*data*.csv"
) -> Dict[Tuple[int, int], Dict[str, Tuple[int, List[Tuple[time, time]]]]]]:

    # Define column name mappings (original -> standardized)
    COLUMN_MAPPING = {
        "Term": "term",
        "Sess": "sess",
        "Bldg": "building",
        "Rm #": "room_number",
        "Rm Cap": "room_cap",
        "Start": "start_time",
        "End": "end_time",
        "Days": "days",
    }

    try:
        # Find the first matching data file
        data_files = list(Path("data").glob(data_file))
        if not data_files:
            raise FileNotFoundError(f"No files matching '{data_file}' found in data directory")
        
        # Read data and standardize column names
        df = pd.read_csv(data_files[0])

        # Print original columns for debugging
        print("Original columns:", df.columns.tolist())

        # Rename columns using the mapping
        df = df.rename(columns=lambda x: COLUMN_MAPPING.get(x, x.lower()))

        # Print renamed columns for debugging
        print("Standardized columns:", df.columns.tolist())

        print("Available columns:", df.columns.tolist())  # Debug
        print("Term values:", df["term"].unique())  # Debug
        print("Session values:", df["sess"].unique())  # Debug
        print("Filtering for term:", term, "session:", session)  # Debug

        # Filter by term and session
        df = df[
            (df["term"] == int(term))
            & (df["sess"] == str(session))  # Using 'sess' consistently
        ]

        print("Filtered DataFrame shape:", df.shape)  # Debug

        # Get dates for requested session
        target_start, target_end = get_dates(term, session)
        if not target_start or not target_end:
            raise ValueError(f"Invalid term/session combination: {term}/{session}")

        target_start_date = parse_date(target_start)
        target_end_date = parse_date(target_end)

        # Filter for overlapping sessions
        overlapping_sessions = []
        for sess in range(1, 5):  # Sessions 1-4
            sess_start, sess_end = get_dates(term, sess)
            if sess_start and sess_end:
                sess_start_date = parse_date(sess_start)
                sess_end_date = parse_date(sess_end)
                if do_dates_overlap(
                    target_start_date, target_end_date, sess_start_date, sess_end_date
                ):
                    overlapping_sessions.append(
                        str(sess)
                    )  # Convert to string to match data

        # Filter for classes in any overlapping session - using 'sess' instead of 'session'
        df = df[df["sess"].isin(overlapping_sessions)]

        # Convert time blocks to time objects
        time_blocks = [
            (parse_time(start), parse_time(end)) for start, end in TIME_BLOCKS
        ]

        # Initialize results with room capacities
        room_caps = {}  # Dictionary to store room capacities
        vacancies = {
            room: {
                day: (0, time_blocks.copy()) for day in days
            }  # (capacity, time_blocks)
            for room in MY_ROOMS
        }

        # First pass: get room capacities
        for _, row in df.iterrows():
            room = (row["building"], row["room_number"])
            if room in MY_ROOMS:
                # Update capacity if it's larger than what we've seen before
                current_cap = vacancies[room][list(vacancies[room].keys())[0]][0]
                new_cap = int(row["room_cap"]) if pd.notna(row["room_cap"]) else 0
                if new_cap > current_cap:
                    for day in days:
                        vacancies[room][day] = (new_cap, vacancies[room][day][1])

        # Second pass: process time blocks
        for _, row in df.iterrows():
            if pd.isna(row["start_time"]) or pd.isna(row["end_time"]):
                continue

            room = (row["building"], row["room_number"])
            if room not in MY_ROOMS:
                continue

            class_time = (parse_time(row["start_time"]), parse_time(row["end_time"]))
            class_days = row["days"]

            for day in days:
                if day in class_days:
                    cap, blocks = vacancies[room][day]
                    vacancies[room][day] = (
                        cap,
                        [
                            block
                            for block in blocks
                            if not is_conflict(class_time, block)
                        ],
                    )

        return vacancies
    except Exception as e:
        print(f"Error in find_vacant_rooms: {e}")
        print(
            f"Term value being searched for: {term}"
        )  # Debug: see what we're searching for
        raise


def get_formatted_blocks(blocks, all_blocks):
    """Convert time blocks to formatted strings, with blanks for occupied times"""
    formatted = []
    blocks_set = set(blocks)  # Convert to set for O(1) lookup

    for block in all_blocks:
        if block in blocks_set:
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
