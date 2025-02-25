# Room capacities stored as {(building, room): capacity}
ROOM_CAPS = {
    (3, 113): 25,
    (5, 103): 30,
    (5, 104): 30,
    (5, 105): 30,
    (5, 106): 30,
    (5, 111): 25,
    (5, 113): 25,
    (5, 211): 30,
    (5, 212): 30,
    (5, 215): 30,
    (9, 230): 40,
    (15, 103): 35,
    (22, 152): 45,
}

def get_room_cap(building: int, room: int) -> int:
    """Get room capacity, return 0 if not found"""
    return ROOM_CAPS.get((building, room), 0) 