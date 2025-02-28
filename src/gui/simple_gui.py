import glob
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import messagebox, ttk

import pandas as pd

from src.core.constants.time_blocks import TIME_BLOCKS
from src.core.room_finder import PROJECT_ROOT, find_vacant_rooms, parse_time

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_data():
    """Load and standardize the DataFrame"""
    data_pattern = str(PROJECT_ROOT / "data" / "*data*.csv")
    matching_files = glob.glob(data_pattern)
    if not matching_files:
        raise FileNotFoundError(f"No data files found matching pattern: {data_pattern}")

    df = pd.read_csv(matching_files[0])  # Use the first matching file
    # print("Original columns:", df.columns.tolist())  # Debug
    df.columns = (
        df.columns.str.lower()
    )  # Standardize all column names to lowercase for safety
    # print("Lowercase columns:", df.columns.tolist())  # Debug
    return df


def get_valid_terms():
    """Get a list of valid terms from the data file"""
    try:
        df = load_data()
        if "term" in df.columns:
            terms = sorted(df["term"].unique().tolist())
            return [str(term) for term in terms]  # Convert to strings for the dropdown
        else:
            print("Warning: 'term' column not found in data file")
            return ["2231"]  # Default fallback
    except Exception as e:
        print(f"Error loading terms: {e}")
        return ["2231"]  # Default fallback


class RoomFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Room Finder")
        self.root.geometry("800x600")

        # Set up the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create input frame
        self.input_frame = ttk.LabelFrame(
            self.main_frame, text="Search Parameters", padding="10"
        )
        self.input_frame.pack(fill=tk.X, pady=10)

        # Term input (dropdown)
        ttk.Label(self.input_frame, text="Term:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )

        # Get available terms
        self.available_terms = get_valid_terms()

        # Create StringVar for the term dropdown
        self.term_var = tk.StringVar()
        if self.available_terms:
            self.term_var.set(
                self.available_terms[0]
            )  # Set default to first available term
        else:
            self.term_var.set("2231")  # Fallback default

        # Create the dropdown
        self.term_dropdown = ttk.Combobox(
            self.input_frame,
            textvariable=self.term_var,
            values=self.available_terms,
            width=10,
            state="readonly",  # Make it read-only so users can only select from the list
        )
        self.term_dropdown.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Days selection
        ttk.Label(self.input_frame, text="Days:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.days_frame = ttk.Frame(self.input_frame)
        self.days_frame.grid(row=1, column=1, sticky=tk.W, pady=5)

        self.day_vars = {}
        self.day_names = {
            "M": "Monday",
            "T": "Tuesday",
            "W": "Wednesday",
            "R": "Thursday",
            "F": "Friday",
            "S": "Saturday",
        }
        days = [
            ("Monday", "M"),
            ("Tuesday", "T"),
            ("Wednesday", "W"),
            ("Thursday", "R"),
            ("Friday", "F"),
            ("Saturday", "S"),
        ]
        for i, (day_name, day_code) in enumerate(days):
            self.day_vars[day_code] = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                self.days_frame, text=day_name, variable=self.day_vars[day_code]
            ).grid(row=0, column=i, padx=5)

        # Search button
        ttk.Button(self.input_frame, text="Search", command=self.search_rooms).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        # Create a frame for the results
        self.results_frame = ttk.LabelFrame(
            self.main_frame, text="Available Time Blocks", padding="10"
        )
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create a frame for the treeview and scrollbar
        tree_frame = ttk.Frame(self.results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create the treeview for time blocks
        self.time_treeview = ttk.Treeview(tree_frame)
        self.time_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.time_treeview.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.time_treeview.configure(yscrollcommand=scrollbar.set)

        # Configure the treeview columns
        self.time_treeview["columns"] = ("time_block", "days", "num_rooms")
        self.time_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the first column
        self.time_treeview.column("time_block", anchor=tk.W, width=150)
        self.time_treeview.column("days", anchor=tk.W, width=150)
        self.time_treeview.column("num_rooms", anchor=tk.CENTER, width=100)

        self.time_treeview.heading("time_block", text="Time Block")
        self.time_treeview.heading("days", text="Days")
        self.time_treeview.heading("num_rooms", text="Available Rooms")

        # Bind the treeview selection event
        self.time_treeview.bind("<<TreeviewSelect>>", self.on_time_block_select)

        # Store the search results
        self.results = {}

        # Dictionary to store time blocks and rooms
        self.common_time_blocks = {}

        # Create a frame for displaying room details
        self.detail_frame = ttk.LabelFrame(
            self.main_frame, text="Available Rooms", padding="10"
        )
        self.detail_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Text widget for displaying room details
        self.detail_text = tk.Text(self.detail_frame, wrap=tk.WORD, height=10)
        self.detail_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Set initial status
        self.status_var.set(
            f"Ready. Found {len(self.available_terms)} terms in data file."
        )

    def search_rooms(self):
        """Search for vacant rooms based on user input"""
        try:
            # Get term from dropdown
            term = int(self.term_var.get())

            # Get selected days
            selected_days = [day for day, var in self.day_vars.items() if var.get()]
            if not selected_days:
                messagebox.showwarning("Warning", "Please select at least one day")
                return

            # Update status
            self.status_var.set("Searching for vacant rooms...")
            self.root.update_idletasks()

            # Call the find_vacant_rooms function
            self.results = find_vacant_rooms(term, selected_days)

            # Clear the treeview
            for item in self.time_treeview.get_children():
                self.time_treeview.delete(item)

            # Find time blocks that are common across all selected days
            self.find_common_time_blocks(selected_days)

            # Clear the detail text
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(
                tk.END, "Select a time block to see available rooms."
            )

            # Update status
            total_rooms = sum(len(rooms) for rooms in self.common_time_blocks.values())
            self.status_var.set(
                f"Found {len(self.common_time_blocks)} time blocks available on all selected days"
            )

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred during search")
            import traceback

            traceback.print_exc()

    def find_common_time_blocks(self, selected_days):
        """Find time blocks that are common across all selected days"""
        # Dictionary to track rooms available at each time block for each day
        time_blocks_by_day = defaultdict(lambda: defaultdict(list))

        # Process each room's vacant times
        for room_key, room_data in self.results.items():
            building, room = room_key.split("-")
            capacity = room_data["capacity"]

            # For each day, add this room to the appropriate time blocks
            for day, times in room_data["vacant_times"].items():
                for start, end in times:
                    time_block = f"{start}-{end}"
                    room_info = {
                        "building": building,
                        "room": room,
                        "capacity": capacity,
                    }
                    time_blocks_by_day[day][time_block].append(room_info)

        # Find time blocks that exist in all selected days
        self.common_time_blocks = {}

        # Get all unique time blocks across all days
        all_time_blocks = set()
        for day in selected_days:
            all_time_blocks.update(time_blocks_by_day[day].keys())

        # For each time block, check if it's available on all selected days
        for time_block in all_time_blocks:
            # Check if this time block exists for all selected days
            if all(time_block in time_blocks_by_day[day] for day in selected_days):
                # Find rooms that are available at this time block on all selected days
                common_rooms = []

                # Start with rooms from the first day
                if selected_days:
                    first_day = selected_days[0]
                    potential_rooms = {
                        (room_info["building"], room_info["room"]): room_info
                        for room_info in time_blocks_by_day[first_day][time_block]
                    }

                    # Check each room against other days
                    for day in selected_days[1:]:
                        day_rooms = {
                            (room_info["building"], room_info["room"])
                            for room_info in time_blocks_by_day[day][time_block]
                        }
                        # Keep only rooms that are also available on this day
                        potential_rooms = {
                            key: value
                            for key, value in potential_rooms.items()
                            if key in day_rooms
                        }

                    # Add the common rooms to our list
                    common_rooms = list(potential_rooms.values())

                if common_rooms:
                    # Format the days string (e.g., "Tuesday, Thursday")
                    days_str = ", ".join(self.day_names[day] for day in selected_days)

                    # Add to treeview
                    self.time_treeview.insert(
                        "",
                        tk.END,
                        values=(time_block, days_str, len(common_rooms)),
                        iid=time_block,
                    )

                    # Store the common rooms for this time block
                    self.common_time_blocks[time_block] = common_rooms

        # Sort the treeview items by start time
        items = [
            (self.time_treeview.item(item, "values"), item)
            for item in self.time_treeview.get_children()
        ]
        items.sort(key=lambda x: parse_time(x[0][0].split("-")[0]))

        # Reinsert items in sorted order
        for values, item in items:
            self.time_treeview.move(item, "", "end")

    def on_time_block_select(self, event):
        """Handle time block selection event"""
        selected_items = self.time_treeview.selection()
        if not selected_items:
            return

        time_block = selected_items[0]

        # Make sure the time block exists in our data
        if time_block not in self.common_time_blocks:
            return

        # Get the rooms for this time block
        rooms = self.common_time_blocks[time_block]

        # Clear the detail text
        self.detail_text.delete(1.0, tk.END)

        # Get the selected days
        selected_days = [day for day, var in self.day_vars.items() if var.get()]
        days_str = ", ".join(self.day_names[day] for day in selected_days)

        # Display the time block and days
        self.detail_text.insert(
            tk.END, f"Available Rooms for {time_block} on {days_str}:\n\n"
        )

        # Sort rooms by building and room number
        sorted_rooms = sorted(rooms, key=lambda x: (int(x["building"]), int(x["room"])))

        # Display the rooms
        for room_info in sorted_rooms:
            building = room_info["building"]
            room = room_info["room"]
            capacity = room_info["capacity"]
            self.detail_text.insert(
                tk.END, f"Building {building}, Room {room} (Capacity: {capacity})\n"
            )


def main():
    root = tk.Tk()
    app = RoomFinderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
