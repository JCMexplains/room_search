# List of tuples containing (Building, Room) pairs
# Both Building and Room are represented as integers

MY_ROOMS = [
    (3, 113),
    (5, 103),
    (5, 104),
    (5, 105),
    (5, 106),
    (5, 111),
    (5, 113),
    (5, 211),
    (5, 212),
    (5, 215),
    (9, 230),
    (15, 103),
    (22, 152),
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
