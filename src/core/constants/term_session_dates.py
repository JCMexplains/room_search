from typing import List, Tuple
from datetime import time
from src.utils.date_utils import parse_time
# Define which sessions overlap with each session
# This follows the diagram in the image
SESSION_OVERLAPS = {
    # For each session, list the sessions that overlap with it
    1: [1],           # Session 1 (full term) only overlaps with itself
    2: [1, 2],        # Session 2 (first half) overlaps with Session 1 and itself
    3: [1, 3],        # Session 3 (middle part) overlaps with Session 1 and itself
    4: [1, 3, 4],     # Session 4 (second half) overlaps with Sessions 1, 3, and itself
}

# For summer term
SUMMER_SESSION_OVERLAPS = {
    1: [1],           # Session 1 (full summer) only overlaps with itself
    2: [1, 2],        # Session 2 (first half) overlaps with Session 1 and itself
    3: [1, 3],        # Session 3 (second half) overlaps with Session 1 and itself
}

def get_overlapping_sessions(session: int, is_summer: bool = False) -> List[int]:
    """
    Get a list of sessions that overlap with the given session.
    
    Args:
        session: The session number (integer)
        is_summer: Whether this is a summer term (default: False)
    
    Returns:
        A list of session numbers that overlap with the given session
    """
    try:
        session = int(session)
        if is_summer:
            return SUMMER_SESSION_OVERLAPS.get(session, [])
        else:
            return SESSION_OVERLAPS.get(session, [])
    except ValueError:
        return []

def is_summer_term(term: int) -> bool:
    """
    Determine if a term is a summer term based on its code.
    
    Args:
        term: The term code (integer)
        
    Returns:
        True if it's a summer term, False otherwise
    """
    # Convert to string and check if the last digit is 3
    # (assuming term codes end with 1=Fall, 2=Spring, 3=Summer)
    try:
        term_str = str(term)
        return term_str[-1] == '3'
    except (ValueError, IndexError):
        return False

def get_formatted_blocks(blocks, all_blocks, session_dates):
    """Convert time blocks to formatted strings, with blanks for occupied times"""
    formatted = []
    
    # Convert blocks to comparable format
    blocks_set = {
        (parse_time(start).time(), parse_time(end).time())
        for start, end in blocks
    }
    
    for block in all_blocks:
        if any(is_conflict(block, class_block) for class_block in blocks_set):
            # Room is occupied - show blank space
            formatted.append(" " * 11)  # Same width as "HH:MM-HH:MM"
        else:
            # Room is vacant - show the time
            formatted.append(f"{block[0].strftime('%H:%M')}-{block[1].strftime('%H:%M')}")
        formatted.append("   ")  # Add 3 spaces of padding between blocks
    
    # Remove the trailing padding from the last block
    if formatted:
        formatted.pop()
    
    return formatted

def is_conflict(class_time: Tuple[time, time], block_time: Tuple[time, time]) -> bool:
    class_start, class_end = class_time
    block_start, block_end = block_time
    return (class_start < block_end) and (block_start < class_end)

def check_overlaps(blocks, session_dates):
    for block in blocks:
        print(f"Checking block {block} against session dates {session_dates}")
        # Logic to check overlaps
