"""
Constants for my preferred rooms.
"""

# List of rooms to check for vacancy
# Format: List of tuples (building_number, room_number)
MY_ROOMS = [
    (1, 101),
    (1, 102),
    (1, 103),
    (2, 201),
    (2, 202),
    (3, 301),
    (3, 302),
]


def is_valid_room(building: int, room: int) -> bool:
    """
    Check if a given building and room combination is in the MY_ROOMS list.

    Args:
        building (int): The building number.
        room (int): The room number.

    Returns:
        bool: True if the combination is in MY_ROOMS, False otherwise.

    Example:
        >>> is_valid_room(3, 113)
        True
        >>> is_valid_room(1, 101)
        False
    """
    return (building, room) in MY_ROOMS
