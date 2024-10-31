from datetime import datetime, time
from typing import List, Tuple, Dict, Set
import pandas as pd

from constants.my_rooms import MY_ROOMS
from constants.time_blocks import TIME_BLOCKS

def parse_time(time_str: str) -> time:
    return datetime.strptime(time_str, "%H:%M").time()

def is_conflict(class_time: Tuple[time, time], block_time: Tuple[time, time]) -> bool:
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

def print_vacancies(vacancies: Dict[Tuple[int, int], Dict[str, List[Tuple[time, time]]]]):
    for room, days in vacancies.items():
        print(f"\nBuilding {room[0]}, Room {room[1]}:")
        for day, blocks in days.items():
            if blocks:  # Only show days with available slots
                times = [f"{block[0].strftime('%H:%M')}-{block[1].strftime('%H:%M')}" 
                        for block in blocks]
                print(f"{day}: {', '.join(times)}") 