import pandas as pd


def process_room_number(room):
    if pd.isna(room):
        return pd.NA
    try:
        room_float = float(room)
        room_int = int(room_float)
        if room_int % 10 == 0 and room_int != 0:
            return room_int // 10
        else:
            return room_int
    except ValueError:
        return pd.NA


def drop_rows(df: pd.DataFrame) -> pd.DataFrame:

    # Check if 'days' column exists
    if "days" in df.columns:
        # Drop rows where 'days' is empty or equals ONLINE
        df = df.dropna(subset=["days"])
        df = df[(df["days"] != "") & (df["days"] != "ONLINE")]
    else:
        print("Warning: 'days' column not found in DataFrame")

    # Check if 'campus' column exists
    if "campus" in df.columns:
        # Drop rows where 'campus' is not 'Central'
        df = df[df["campus"] == "Central"]
    else:
        print("Warning: 'campus' column not found in DataFrame")

    # Check if 'building' column exists
    if "building" in df.columns:
        # Drop rows where 'building' is 'TBA'
        df = df[df["building"] != "TBA"]
    else:
        print("Warning: 'building' column not found in DataFrame")

    # Check if 'start_time' column exists
    if "start_time" in df.columns:
        # Drop rows where 'start_time' is 'TBA'
        df = df[df["start_time"] != "TBA"]
    else:
        print("Warning: 'start_time' column not found in DataFrame")

    # Check if 'room_number' column exists
    if "room_number" in df.columns:
        # Process room_number
        df["room_number"] = df["room_number"].apply(process_room_number)
        df["room_number"] = pd.to_numeric(df["room_number"], errors="coerce").astype("Int64")
        # Drop rows where 'room_number' is null after processing
        df = df.dropna(subset=["room_number"])
    else:
        print("Warning: 'room_number' column not found in DataFrame")

    return df
