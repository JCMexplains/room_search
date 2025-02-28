# Room capacities stored as {(building, room): capacity}
ROOM_CAPS = {
    (3, 113): 32,
    (5, 103): 25,
    (5, 104): 25,
    (5, 105): 25,
    (5, 106): 30,
    (5, 107): 30,
    (5, 108): 30,
    (5, 109): 15,
    (5, 111): 25,
    (5, 112): 25,
    (5, 115): 28,
    (5, 201): 30,
    (5, 203): 30,
    (5, 204): 25,
    (5, 211): 20,
    (5, 212): 25,
    (5, 213): 20,
    (5, 215): 30,
    (9, 230): 40,
    (15, 103): 25,
    (22, 152): 35,
}


def get_room_cap(building: int, room: int) -> int:
    """Get room capacity, raises KeyError if not found"""
    if (building, room) not in ROOM_CAPS:
        raise KeyError(
            f"Room {room} in building {building} not found in room capacity data"
        )
    return ROOM_CAPS[(building, room)]
