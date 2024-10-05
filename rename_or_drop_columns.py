import re

import pandas as pd
import pytest


def camel_to_snake(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower().replace(" ", "_").replace("__", "_")


def process_dataframe(df):
    # Strip whitespace from column names and convert to snake_case
    df.columns = [camel_to_snake(col.strip()) for col in df.columns]

    column_mapping = {
        "act_cntct_hrs": None,
        "bldg": "building",
        "campus": "campus",
        "campus_code": None,
        "class_title": None,
        "cls_max": None,
        "cost_center": None,
        "course_description": None,
        "course_id": "course_id",
        "credit_hrs": None,
        "credit_type": None,
        "days": "days",
        "department": "department",
        "designators": None,
        "division": "division",
        "end": "end_time",
        "enrolled": None,
        "enr/_max": None,
        "f/p/e": None,
        "fees": None,
        "fte": None,
        "grades": None,
        "grades_entered": None,
        "instructor_name": "instructor_name",
        "max/_cap": None,
        "outlier": None,
        "paid": None,
        "paid_fte": None,
        "pay": None,
        "pd/_enr": None,
        "ref_num": "reference_number",
        "rm_cap": "room_cap",
        "rm_#": "room_number",
        "schedule_notes": None,
        "sess": "session",
        "start": "start_time",
        "std_cntct_hrs": None,
        "term": "term",
    }

    # Rename columns (only for existing columns)
    df = df.rename(
        columns={
            col: new_name
            for col, new_name in column_mapping.items()
            if col in df.columns and new_name is not None
        }
    )

    # Drop columns (only existing columns that are mapped to None)
    columns_to_drop = [
        col
        for col in df.columns
        if col in column_mapping and column_mapping[col] is None
    ]
    df = df.drop(columns=columns_to_drop)

    # Sort the columns alphabetically
    df = df.reindex(sorted(df.columns), axis=1)

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object"]):
        df[col] = df[col].str.strip()

    return df
