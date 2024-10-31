import json
import os
import tkinter as tk
from tkinter import ttk
from typing import Dict, Tuple, Set, List
from datetime import time, datetime
import pandas as pd



class RoomSearchGUI:
    def __init__(
        self,
        master: tk.Tk,
        unoccupied_slots: Dict[Tuple[int, int], Dict[str, Set[Tuple[time, time]]]],
        room_capacities: Dict[Tuple[int, int], int],
        semester_blocks: List[Tuple[time, time]],
        my_rooms: List[Tuple[int, int]]
    ) -> None:
        self.master = master
        self.unoccupied_slots = unoccupied_slots
        self.room_capacities = room_capacities
        self.semester_blocks = semester_blocks
        self.my_rooms = my_rooms
        master.title("Room Search")

        self.settings_file = os.path.join("data", "gui_settings.txt")

        # Initialize frames in correct order
        self.init_days_frame()
        self.init_time_slots_frame()  # Create time_slots_frame before terms frame
        self.init_terms_frame()       # This will update the time slots
        self.init_rooms_frame()

        self.load_settings()

        # Submit Button
        self.submit_button = ttk.Button(
            master, text="Find Unoccupied Rooms", command=self.submit
        )
        self.submit_button.pack(pady=20)

    def init_days_frame(self):
        self.days_frame = ttk.LabelFrame(self.master, text="Days")
        self.days_frame.pack(padx=10, pady=10, fill="x")
        self.days = ["M", "T", "W", "R", "F", "S"]
        self.day_vars = {}
        for day in self.days:
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.days_frame, text=day, variable=var).pack(side="left")
            self.day_vars[day] = var

    def init_rooms_frame(self):
        self.rooms_frame = ttk.LabelFrame(self.master, text="Rooms")
        self.rooms_frame.pack(padx=10, pady=10, fill="x")
        self.room_vars = {}
        for building, room in self.my_rooms:
            var = tk.BooleanVar(value=True)
            capacity = self.room_capacities.get((building, room), "N/A")
            room_text = f"{building}-{room} (Cap: {capacity})"
            ttk.Checkbutton(
                self.rooms_frame, 
                text=room_text, 
                variable=var
            ).pack(anchor="w")
            self.room_vars[(building, room)] = var

    def init_time_slots_frame(self):
        self.time_slots_frame = ttk.LabelFrame(self.master, text="Time Slots")
        self.time_slots_frame.pack(padx=10, pady=10, fill="x")
        self.time_slot_vars = {}

    def update_time_slots(self, *args):
        # Clear existing time slots
        for widget in self.time_slots_frame.winfo_children():
            widget.destroy()
        
        # Determine if summer term
        selected_term = int(self.selected_term.get())
        is_summer_term = str(selected_term).endswith('3')
        
        # Get appropriate blocks
        from constants.time_blocks import summer_blocks, fall_spring_blocks
        blocks = summer_blocks if is_summer_term else fall_spring_blocks
        
        # Convert blocks to time objects
        from find_unoccupied_rooms import convert_to_time_tuples
        time_blocks = convert_to_time_tuples(blocks)
        
        # Create new checkboxes
        self.time_slot_vars = {}
        for start, end in time_blocks:
            var = tk.BooleanVar(value=True)
            time_slot_text = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
            ttk.Checkbutton(
                self.time_slots_frame,
                text=time_slot_text,
                variable=var
            ).pack(anchor="w")
            self.time_slot_vars[(start, end)] = var

    def init_terms_frame(self):
        self.terms_frame = ttk.LabelFrame(self.master, text="Term")
        self.terms_frame.pack(padx=10, pady=10, fill="x")
        
        # Read terms from the CSV file
        df = pd.read_csv(os.path.join("data", "data.csv"))
        self.available_terms = sorted(df['term'].unique())
        
        # Create StringVar for the combobox
        self.selected_term = tk.StringVar()
        if self.available_terms:
            self.selected_term.set(str(self.available_terms[0]))  # Set default value
            self.update_time_slots()  # Initialize time slots based on default term
        
        # Create and pack the combobox
        self.term_combo = ttk.Combobox(
            self.terms_frame, 
            textvariable=self.selected_term,
            values=[str(term) for term in self.available_terms],
            state="readonly"
        )
        self.term_combo.pack(padx=5, pady=5)

    def submit(self) -> None:
        selected_days = [day for day, var in self.day_vars.items() if var.get()]
        selected_rooms = [room for room, var in self.room_vars.items() if var.get()]
        selected_time_slots = [slot for slot, var in self.time_slot_vars.items() if var.get()]
        selected_term = int(self.selected_term.get())

        self.save_settings()

        # Filter unoccupied_slots based on selections
        filtered_slots = self.filter_unoccupied_slots(
            selected_days, 
            selected_rooms, 
            selected_time_slots,
            selected_term
        )

        # Display results
        self.display_results(filtered_slots)

    def filter_unoccupied_slots(
        self,
        selected_days: List[str],
        selected_rooms: List[Tuple[int, int]],
        selected_time_slots: List[Tuple[time, time]],
        selected_term: int
    ) -> Dict[Tuple[int, int], Dict[str, Set[Tuple[time, time]]]]:
        filtered = {}
        for (building, room), days in self.unoccupied_slots.items():
            if (building, room) in selected_rooms:
                filtered[(building, room)] = {}
                for day, slots in days.items():
                    if day in selected_days:
                        filtered[(building, room)][day] = set(
                            slot for slot in slots 
                            if slot in selected_time_slots
                        )
        return filtered

    def save_settings(self) -> None:
        settings = {
            "days": {day: var.get() for day, var in self.day_vars.items()},
            "rooms": {
                f"{building},{room}": var.get()
                for (building, room), var in self.room_vars.items()
            },
            "time_slots": {
                f"{start.strftime('%H:%M')},{end.strftime('%H:%M')}": var.get()
                for (start, end), var in self.time_slot_vars.items()
            },
            "term": self.selected_term.get()
        }
        with open(self.settings_file, "w") as f:
            json.dump(settings, f)

    def load_settings(self) -> None:
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                settings = json.load(f)

            for day, value in settings.get("days", {}).items():
                if day in self.day_vars:
                    self.day_vars[day].set(value)

            for room_key, value in settings.get("rooms", {}).items():
                try:
                    building, room = map(int, room_key.split(","))
                    if (building, room) in self.room_vars:
                        self.room_vars[(building, room)].set(value)
                except ValueError:
                    pass

            for time_slot_key, value in settings.get("time_slots", {}).items():
                try:
                    start_str, end_str = time_slot_key.split(",")
                    start = datetime.strptime(start_str, "%H:%M").time()
                    end = datetime.strptime(end_str, "%H:%M").time()
                    if (start, end) in self.time_slot_vars:
                        self.time_slot_vars[(start, end)].set(value)
                except ValueError:
                    pass

            # Load term setting
            saved_term = settings.get("term")
            if saved_term and saved_term in [str(term) for term in self.available_terms]:
                self.selected_term.set(saved_term)

    def display_results(self, unoccupied_slots: Dict[Tuple[int, int], Dict[str, Set[Tuple[time, time]]]]) -> None:
        # Create a new window to display results
        results_window = tk.Toplevel(self.master)
        results_window.title("Unoccupied Rooms")

        # Create a text widget to display results
        text_widget = tk.Text(results_window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH)

        # Insert results into the text widget
        for (building, room), days in unoccupied_slots.items():
            text_widget.insert(tk.END, f"\nBuilding {building}, Room {room}:\n")
            for day, unoccupied_blocks in days.items():
                text_widget.insert(tk.END, f"  {day} unoccupied time blocks:\n")
                if unoccupied_blocks:
                    for start, end in sorted(unoccupied_blocks):
                        text_widget.insert(
                            tk.END,
                            f"    {start.strftime('%H:%M')} - {end.strftime('%H:%M')}\n",
                        )
                else:
                    text_widget.insert(tk.END, "    Fully occupied\n")

        # Make the text widget read-only
        text_widget.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    gui = RoomSearchGUI(root, {}, {}, [], [])
    root.mainloop()


