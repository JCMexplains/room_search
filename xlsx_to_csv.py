import re
import warnings
import pandas as pd
from pathlib import Path


from constants.term_session_dates import TERM_SESSION_DATES, get_dates
from drop_rows import drop_rows
from rename_or_drop_columns import process_dataframe


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object"]):
        df[col] = df[col].str.strip()

    return df


def process_room_number(room: str | float | int) -> int | None:
    """
    This function does two things: it ensures that a string or float is converted to an integer, and it removes the final digit if it is 0.

    All the room numbers from CID are padded with a final 0, which we want to remove.

    Args:
        room: str | float | int: The input room number, which can be a string, float, or integer.

    Returns:
        int | None: The processed room number as an integer, or None if the input is invalid or cannot be processed.

    Examples:
        >>> process_room_number("103")
        103
        >>> process_room_number(10.0)
        1
        >>> process_room_number("invalid")
        None
    """
    if pd.isna(room):
        return None
    try:
        room_float = float(room)
        room_int = int(room_float)
        if room_int % 10 == 0 and room_int != 0:
            return room_int // 10
        else:
            return room_int
    except ValueError:
        return None


def transform_xlsx_to_csv(input_file: str | Path, output_file: str | Path) -> None:
    # Suppress the warning that we don't have a default style sheet
    warnings.filterwarnings(
        "ignore", category=UserWarning, module="openpyxl.styles.stylesheet"
    )

    # Read the Excel file
    df = pd.read_excel(input_file)

    # Process the DataFrame (rename/drop columns)
    df = process_dataframe(df)

    # Ensure specific columns are integers
    integer_columns = ["reference_number", "room_cap", "session", "term"]
    for col in integer_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        else:
            print(f"Column '{col}' not found in the DataFrame")

    # trim campus, department, and division fields using regex
    for col in ["campus", "department", "division"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: re.sub(r"\s.*$", "", str(x)))
        else:
            print(f"Column '{col}' not found in the DataFrame")

    # Process room_number
    if "room_number" in df.columns:
        df["room_number"] = df["room_number"].apply(process_room_number)
        df["room_number"] = pd.to_numeric(df["room_number"], errors="coerce").astype("Int64")
    else:
        print("Warning: 'room_number' column not found in DataFrame")

    # Call drop_rows function from drop_rows.py
    df = drop_rows(df)

    # Convert 'start_time' and 'end_time' to time only (HH:MM format)
    def format_time(x):
        if pd.isna(x) or x == "TBA":
            return x
        try:
            return pd.to_datetime(x).strftime("%H:%M")
        except:
            return x

    for col in ["start_time", "end_time"]:
        if col in df.columns:
            df[col] = df[col].apply(format_time)
        else:
            print(f"Column '{col}' not found in the DataFrame")

    date_pairs = df.apply(lambda row: get_dates(row["term"], row["session"]), axis=1)
    # print("Debug: date_pairs =", date_pairs)
    if not date_pairs.empty:
        df["start_date"], df["end_date"] = zip(
            *[(pair if pair is not None else (None, None)) for pair in date_pairs]
        )
    else:
        print("Warning: date_pairs is empty")
        df["start_date"] = None
        df["end_date"] = None

    # Sort the columns alphabetically
    # this puts start_date and end_date in the right place; the list was already sorted in rename_or_drop_columns.py
    df = df.reindex(sorted(df.columns), axis=1)

    # Write the transformed data to a CSV file
    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    current_dir = Path(__file__).parent
    data_dir = current_dir / "data"
    input_xlsx = data_dir / "data.xlsx"
    output_csv = data_dir / "data.csv"
    transform_xlsx_to_csv(input_xlsx, output_csv)
