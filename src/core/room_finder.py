from datetime import datetime, time, date
from typing import List, Tuple, Dict, Set, Optional
import pandas as pd
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('room_finder.log'),
        logging.StreamHandler()
    ]
)

from src.core.constants.my_rooms import MY_ROOMS
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
    
    return (block_start <= class_start <= block_end or 
            block_start <= class_end <= block_end or
            class_start <= block_start <= class_end)

def find_vacant_rooms(
    term: int,
    session: int,
    days: List[str],
    data_file: str = "data.csv"
) -> Dict[Tuple[int, int], Dict[str, List[Tuple[time, time]]]]:
    
    logging.info(f"Starting room search for term {term}, session {session}, days {days}")
    
    # Validate input file
    data_path = Path("data") / data_file
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    try:
        # Read and prepare data
        df = pd.read_csv(f"data/{data_file}")
        df = df[
            (df['term'] == term) & 
            (df['session'] == session)
        ]

        # Convert time blocks to time objects
        time_blocks = [(parse_time(start), parse_time(end)) for start, end in TIME_BLOCKS]
        
        # Initialize results
        vacancies = {
            room: {day: time_blocks.copy() for day in days}
            for room in MY_ROOMS
        }

        # Process each class
        for _, row in df.iterrows():
            if pd.isna(row['start_time']) or pd.isna(row['end_time']):
                continue
                
            room = (row['building'], row['room_number'])
            if room not in MY_ROOMS:
                continue
                
            class_time = (parse_time(row['start_time']), parse_time(row['end_time']))
            class_days = row['days']
            
            for day in days:
                if day in class_days:
                    vacancies[room][day] = [
                        block for block in vacancies[room][day]
                        if not is_conflict(class_time, block)
                    ]

        return vacancies
    except Exception as e:
        logging.error(f"An error occurred while searching for vacant rooms: {e}")
        raise

def print_vacancies(vacancies: Dict[Tuple[int, int], Dict[str, List[Tuple[time, time]]]]):
    for room, days in vacancies.items():
        print(f"\nBuilding {room[0]}, Room {room[1]}:")
        for day, blocks in days.items():
            if blocks:  # Only show days with available slots
                times = [f"{block[0].strftime('%H:%M')}-{block[1].strftime('%H:%M')}" 
                        for block in blocks]
                print(f"{day}: {', '.join(times)}") 