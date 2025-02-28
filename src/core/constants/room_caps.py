"""
Constants for room capacities.
"""

# Dictionary mapping (building, room) to capacity
ROOM_CAPACITIES = {
    (1, 101): 30,
    (1, 102): 25,
    (1, 103): 40,
    (2, 201): 50,
    (2, 202): 35,
    (3, 301): 60,
    (3, 302): 45,
}


def get_room_cap(building, room):
    """Get the capacity of a room"""
    return ROOM_CAPACITIES.get((building, room), 0)
