import tkinter as tk
from tkinter import ttk
import json
import os
from my_rooms import MY_ROOMS, get_room_capacity
from find_unoccupied_rooms import find_unoccupied_rooms

class RoomSearchGUI:
    def __init__(self, master):
        self.master = master
        master.title("Room Search")

        self.settings_file = os.path.join(os.path.dirname(__file__), 'data', 'settings.txt')
        self.load_settings()

        # Days
        self.days_frame = ttk.LabelFrame(master, text="Days")
        self.days_frame.pack(padx=10, pady=10, fill="x")
        self.days = ["M", "T", "W", "R", "F", "S"]
        self.day_vars = {}
        for day in self.days:
            var = tk.BooleanVar(value=self.settings['days'].get(day, True))
            ttk.Checkbutton(self.days_frame, text=day, variable=var, command=self.save_settings).pack(side="left")
            self.day_vars[day] = var

        # Rooms
        self.rooms_frame = ttk.LabelFrame(master, text="Rooms")
        self.rooms_frame.pack(padx=10, pady=10, fill="x", expand=True)
        self.room_vars = {}
        
        # Create a canvas with a scrollbar for the rooms
        self.canvas = tk.Canvas(self.rooms_frame)
        self.scrollbar = ttk.Scrollbar(self.rooms_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        for building, room, _ in MY_ROOMS:
            var = tk.BooleanVar(value=self.settings['rooms'].get(f"{building}-{room}", True))
            capacity = get_room_capacity(building, room)
            ttk.Checkbutton(
                self.scrollable_frame, 
                text=f"Building {building}, Room {room} (Capacity: {capacity})", 
                variable=var,
                command=self.save_settings
            ).pack(anchor="w")
            self.room_vars[(building, room)] = var

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Submit Button
        self.submit_button = ttk.Button(
            master, text="Find Unoccupied Rooms", command=self.submit
        )
        self.submit_button.pack(pady=20)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {'days': {}, 'rooms': {}}

    def save_settings(self):
        settings = {
            'days': {day: var.get() for day, var in self.day_vars.items()},
            'rooms': {f"{building}-{room}": var.get() for (building, room), var in self.room_vars.items()}
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)

    def submit(self):
        selected_days = [day for day, var in self.day_vars.items() if var.get()]
        selected_rooms = [room for room, var in self.room_vars.items() if var.get()]

        # Call find_unoccupied_rooms with these selections
        unoccupied_slots = find_unoccupied_rooms(selected_days, selected_rooms)

        # Display results
        self.display_results(unoccupied_slots)

    def display_results(self, unoccupied_slots):
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
    gui = RoomSearchGUI(root)
    root.mainloop()
