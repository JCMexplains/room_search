import glob
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import pandas as pd

from src.core.constants.time_blocks import TIME_BLOCKS
from src.core.room_finder import (
    PROJECT_ROOT,
    find_vacant_rooms,
    get_formatted_blocks,
    parse_time,
)
from src.utils.settings import load_settings, save_settings

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
        self.root.geometry("800x600")

        # Set up the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create input frame
        self.input_frame = ttk.LabelFrame(
            self.main_frame, text="Search Parameters", padding="10"
        )
        self.input_frame.pack(fill=tk.X, pady=10)

        # Term input
        ttk.Label(self.input_frame, text="Term:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.term_var = tk.StringVar(value="2231")  # Default to Fall 2023
        ttk.Entry(self.input_frame, textvariable=self.term_var, width=10).grid(
            row=0, column=1, sticky=tk.W, pady=5
        )

        # Days selection
        ttk.Label(self.input_frame, text="Days:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.days_frame = ttk.Frame(self.input_frame)
        self.days_frame.grid(row=1, column=1, sticky=tk.W, pady=5)

        self.day_vars = {}
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

        # Results frame
        self.results_frame = ttk.LabelFrame(
            self.main_frame, text="Results", padding="10"
        )
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create a frame for the treeview and scrollbar
        tree_frame = ttk.Frame(self.results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create the treeview
        self.tree = ttk.Treeview(tree_frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configure the treeview columns
        self.tree["columns"] = ("building", "room", "capacity")
        self.tree.column("#0", width=0, stretch=tk.NO)  # Hide the first column
        self.tree.column("building", anchor=tk.W, width=80)
        self.tree.column("room", anchor=tk.W, width=80)
        self.tree.column("capacity", anchor=tk.W, width=80)

        self.tree.heading("building", text="Building")
        self.tree.heading("room", text="Room")
        self.tree.heading("capacity", text="Capacity")

        # Bind the treeview selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Create a frame for displaying room details
        self.detail_frame = ttk.LabelFrame(
            self.main_frame, text="Room Details", padding="10"
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

        # Store the search results
        self.results = {}

    def search_rooms(self):
        """Search for vacant rooms based on user input"""
        try:
            # Get term from input
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
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Populate the treeview with results
            for room_key, room_data in self.results.items():
                building, room = room_key.split("-")
                capacity = room_data["capacity"]
                self.tree.insert(
                    "", tk.END, values=(building, room, capacity), iid=room_key
                )

            # Update status
            self.status_var.set(f"Found {len(self.results)} rooms")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred during search")

    def on_tree_select(self, event):
        """Handle treeview selection event"""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        room_key = selected_items[0]
        room_data = self.results.get(room_key)
        if not room_data:
            return

        # Clear the detail text
        self.detail_text.delete(1.0, tk.END)

        # Get building and room from the key
        building, room = room_key.split("-")

        # Display room details
        self.detail_text.insert(tk.END, f"Building: {building}\n")
        self.detail_text.insert(tk.END, f"Room: {room}\n")
        self.detail_text.insert(tk.END, f"Capacity: {room_data['capacity']}\n\n")

        # Display vacant times for each day
        self.detail_text.insert(tk.END, "Vacant Times:\n")
        for day, times in room_data["vacant_times"].items():
            day_names = {
                "M": "Monday",
                "T": "Tuesday",
                "W": "Wednesday",
                "R": "Thursday",
                "F": "Friday",
                "S": "Saturday",
            }
            day_name = day_names.get(day, day)
            self.detail_text.insert(tk.END, f"{day_name}: ")

            if times:
                # Format the times
                formatted_times = []
                for start, end in times:
                    formatted_times.append(f"{start}-{end}")
                self.detail_text.insert(tk.END, ", ".join(formatted_times))
            else:
                self.detail_text.insert(tk.END, "No vacant times")

            self.detail_text.insert(tk.END, "\n")


def main():
    root = tk.Tk()
    app = RoomFinderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
