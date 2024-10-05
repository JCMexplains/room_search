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


def is_valid_room(building, room):
    """
    Check if a given building and room combination is in the MY_ROOMS list.

    :param building: The building number (integer)
    :param room: The room number (integer)
    :return: True if the combination is in MY_ROOMS, False otherwise
    """
    return (building, room) in MY_ROOMS
