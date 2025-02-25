import glob
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import pandas as pd

from src.core.constants.time_blocks import TIME_BLOCKS
from src.core.room_finder import PROJECT_ROOT, find_vacant_rooms, get_formatted_blocks
from src.utils.date_utils import parse_time
from src.utils.settings import load_settings, save_settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_data():
    """Load and standardize the DataFrame"""
    data_pattern = str(PROJECT_ROOT / "data" / "*data*.csv")
    matching_files = glob.glob(data_pattern)
    if not matching_files:
        raise FileNotFoundError(f"No data files found matching pattern: {data_pattern}")

    df = pd.read_csv(matching_files[0])  # Use the first matching file
    print("Original columns:", df.columns.tolist())  # Debug
    df.columns = df.columns.str.lower()  # Standardize all column names to lowercase
    print("Lowercase columns:", df.columns.tolist())  # Debug
    return df


def get_valid_terms():
    try:
        df = load_data()
        return sorted(df["term"].unique().tolist())
    except Exception as e:
        print(f"Error loading data: {e}")
        return []


class RoomFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Room Finder")

        # Get valid terms from CSV
        self.valid_terms = get_valid_terms()
        self.valid_sessions = [1, 2, 3, 4]

        # Load saved settings
        settings = load_settings()

        # Term/Session Frame
        frame = ttk.LabelFrame(root, text="Term & Session", padding=10)
        frame.pack(fill="x", padx=5, pady=5)

        # Term Dropdown
        ttk.Label(frame, text="Term:").pack(side="left")
        self.term_var = tk.StringVar(value=settings["term"] or str(self.valid_terms[0]))
        term_dropdown = ttk.Combobox(
            frame,
            textvariable=self.term_var,
            values=self.valid_terms,
            width=10,
            state="readonly",
        )
        term_dropdown.pack(side="left", padx=5)

        # Session Dropdown
        ttk.Label(frame, text="Session:").pack(side="left")
        self.session_var = tk.StringVar(value=settings["session"])
        session_dropdown = ttk.Combobox(
            frame,
            textvariable=self.session_var,
            values=self.valid_sessions,
            width=5,
            state="readonly",
        )
        session_dropdown.pack(side="left", padx=5)

        # Days Frame
        days_frame = ttk.LabelFrame(root, text="Days", padding=10)
        days_frame.pack(fill="x", padx=5, pady=5)

        self.day_vars = {}
        for day in "MTWRFS":
            self.day_vars[day] = tk.BooleanVar(value=settings["days"].get(day, True))
            ttk.Checkbutton(days_frame, text=day, variable=self.day_vars[day]).pack(
                side="left"
            )

        # Search Button
        ttk.Button(root, text="Find Vacant Rooms", command=self.search).pack(pady=10)

        # Results
        self.results = tk.Text(root, height=20, width=60)
        self.results.pack(padx=5, pady=5, fill="both", expand=True)

    def search(self):
        try:
            df = load_data()  # Use the same standardized loading function
            term = self.term_var.get()
            session = self.session_var.get()
            days_state = {day: var.get() for day, var in self.day_vars.items()}

            # Save current settings before search
            save_settings(term, session, days_state)

            # Convert term and session to int for the search
            term = int(term)
            session = int(session)
            days = [day for day, var in self.day_vars.items() if var.get()]

            # Update this to use PROJECT_ROOT
            vacant_rooms = find_vacant_rooms(
                term=term,
                session=session,
                days=days,
                data_file=str(
                    PROJECT_ROOT / "data" / "data.csv"
                ),  # Use absolute path here
            )

            # Get all possible time blocks from constants
            all_blocks = [
                (parse_time(start), parse_time(end)) for start, end in TIME_BLOCKS
            ]

            # Display results with explanation header
            self.results.delete(1.0, tk.END)

            # Add explanation header
            self.results.insert(tk.END, "Room Availability Display:\n")
            self.results.insert(
                tk.END,
                "- Times shown (e.g., '08:00-09:15') indicate the room is VACANT\n",
            )
            self.results.insert(
                tk.END, "- Blank spaces indicate the room is OCCUPIED\n\n"
            )

            # Print header with time blocks
            header_times = [
                f"{block[0].strftime('%H:%M')}-{block[1].strftime('%H:%M')}   "
                for block in all_blocks
            ]
            header_times[-1] = header_times[
                -1
            ].rstrip()  # Remove padding from last block
            self.results.insert(tk.END, "Times: " + "".join(header_times) + "\n")
            self.results.insert(tk.END, "-" * (len(header_times) * 14 + 20) + "\n")

            for room_key, room_data in vacant_rooms.items():
                building, room = room_key.split('-')
                self.results.insert(
                    tk.END,
                    f"\nBuilding {building}, Room {room} (Cap: {room_data['capacity']}):\n",
                )
                for day, times in room_data['vacant_times'].items():
                    formatted_blocks = get_formatted_blocks(times, all_blocks)
                    self.results.insert(
                        tk.END, f"{day:<6}: {''.join(formatted_blocks)}\n"
                    )
        except Exception as e:
            print(f"Error searching: {e}")


def main():
    root = tk.Tk()
    app = RoomFinderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
