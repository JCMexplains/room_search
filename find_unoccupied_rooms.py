from datetime import datetime, time
from typing import List, Tuple

import pandas as pd

from my_rooms import MY_ROOMS
from time_blocks import fall_spring_blocks as fall_spring_blocks_str
from time_blocks import summer_blocks as summer_blocks_str


def convert_to_time_tuples(blocks: List[Tuple[str, str]]) -> List[Tuple[time, time]]:
    return [
        (
            datetime.strptime(start, "%H:%M").time(),
            datetime.strptime(end, "%H:%M").time(),
        )
        for start, end in blocks
    ]


# Convert the imported blocks to datetime.time objects
fall_spring_blocks = convert_to_time_tuples(fall_spring_blocks_str)
summer_blocks = convert_to_time_tuples(summer_blocks_str)


def is_summer(term):
    return str(term).endswith("3")


def class_in_block(class_start, class_end, block_start, block_end):
    # print(
    #     f"Debug: class_start type: {type(class_start)}, class_end type: {type(class_end)}"
    # )
    start_in_block = block_start <= class_start < block_end
    end_in_block = block_start < class_end <= block_end
    spans_block = class_start <= block_start and class_end >= block_end
    return start_in_block or end_in_block or spans_block


def expand_days(days_string):
    return pd.Series(
        {
            day: day in days_string if pd.notna(days_string) else False
            for day in "MTWRFS"
        }
    )


def parse_time(time_str):
    if pd.isna(time_str):
        return None
    time_str = time_str.strip()
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        print(f"Warning: Unable to parse time '{time_str}'. Returning None.")
        return None


def main():
    # Define column types
    dtypes = {
        "building": int,
        "campus": str,
        "course_id": str,
        "days": str,
        "delivery_method": str,
        "department": str,
        "division": str,
        "end_date": str,
        "instructor_name": str,
        "reference_number": int,
        "room_number": int,
        "session": int,
        "start_date": str,
        "start_time": str,
        "end_time": str,  # Changed from str to object
        "term": int,
    }

    # Read CSV file
    df = pd.read_csv(
        "data.csv",
        dtype=dtypes,
        skipinitialspace=True,
    )

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Apply parse_time function to start_time and end_time columns
    df["start_time"] = df["start_time"].apply(parse_time)
    df["end_time"] = df["end_time"].apply(parse_time)

    # Expand the 'days' column
    day_columns = df["days"].apply(expand_days)
    df = pd.concat([df.drop("days", axis=1), day_columns], axis=1)

    # Initialize occupancy dictionary
    occupancy = {
        (building, room): {day: set() for day in "MTWRFS"}
        for building, room in MY_ROOMS
    }

    # Fill occupancy dictionary
    for _, row in df.iterrows():
        building = row["building"]
        room = row["room_number"] if pd.notna(row["room_number"]) else None
        if (building, room) in MY_ROOMS:
            blocks = summer_blocks if is_summer(row["term"]) else fall_spring_blocks

            # Debug print
            # print(
            #     f"Debug: Processing row - Building: {building}, Room: {room}, Start: {row['start_time']}, End: {row['end_time']}"
            # )

            # Check if start_time and end_time are not None
            if row["start_time"] is not None and row["end_time"] is not None:
                for block_start, block_end in blocks:
                    if class_in_block(
                        row["start_time"], row["end_time"], block_start, block_end
                    ):
                        for day in "MTWRFS":
                            if row[day]:
                                occupancy[(building, room)][day].add(
                                    (block_start, block_end)
                                )
                                # print(
                                #     f"Debug: Room {building}-{room} is occupied on {day} at {block_start}-{block_end}"
                                # )
            else:
                print(
                    f"Debug: Skipping row due to None values - Start: {row['start_time']}, End: {row['end_time']}"
                )

    # Find and print unoccupied time slots
    for (building, room), days in occupancy.items():
        print(f"\nBuilding {building}, Room {room}:")
        for day, occupied_blocks in days.items():
            print(f"  {day} unoccupied time blocks:")
            all_blocks = (
                summer_blocks
                if any(is_summer(term) for term in df["term"])
                else fall_spring_blocks
            )
            unoccupied = set(all_blocks) - occupied_blocks
            if unoccupied:
                for start, end in sorted(unoccupied):
                    print(f"    {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
            else:
                print("    Fully occupied")


if __name__ == "__main__":
    main()
