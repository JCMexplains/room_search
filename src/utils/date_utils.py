from datetime import datetime, time, date
from typing import Optional, Tuple
import logging

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
