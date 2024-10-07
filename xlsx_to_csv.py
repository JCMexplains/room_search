import re
import warnings

import pandas as pd
from openpyxl import styles

from drop_rows import drop_rows
from rename_or_drop_columns import process_dataframe
from constants.term_session_dates import TERM_SESSION_DATES, get_dates


def clean_dataframe(df):
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object"]):
        df[col] = df[col].str.strip()

    return df


def transform_xlsx_to_csv(input_file, output_file):
    # Suppress the specific warning
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

    # Call drop_rows function from drop_rows.py
    # also deletes trailing zeroes from room numbers
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
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_xlsx = os.path.join(current_dir, "data.xlsx")
    output_csv = os.path.join(current_dir, "data.csv")
    transform_xlsx_to_csv(input_xlsx, output_csv)
