import tkinter as tk
from tkinter import ttk

import find_unoccupied_rooms
from my_rooms import MY_ROOMS
from time_blocks import fall_spring_blocks, summer_blocks


class RoomSearchGUI:
    def __init__(self, master):
        self.master = master
        master.title("Room Search")

        # Days
        self.days_frame = ttk.LabelFrame(master, text="Days")
        self.days_frame.pack(padx=10, pady=10, fill="x")
        self.days = ["M", "T", "W", "R", "F"]
        self.day_vars = {}
        for day in self.days:
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.days_frame, text=day, variable=var).pack(side="left")
            self.day_vars[day] = var

        # Rooms
        self.rooms_frame = ttk.LabelFrame(master, text="Rooms")
        self.rooms_frame.pack(padx=10, pady=10, fill="x")
        self.room_vars = {}
        for building, room in MY_ROOMS:
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                self.rooms_frame, text=f"{building}-{room}", variable=var
            ).pack(anchor="w")
            self.room_vars[(building, room)] = var

        # Time Blocks
        self.blocks_frame = ttk.LabelFrame(master, text="Time Blocks")
        self.blocks_frame.pack(padx=10, pady=10, fill="x")
        self.block_vars = {}
        for start, end in fall_spring_blocks:
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                self.blocks_frame, text=f"{start}-{end}", variable=var
            ).pack(anchor="w")
            self.block_vars[(start, end)] = var

        # Submit Button
        self.submit_button = ttk.Button(
            master, text="Find Unoccupied Rooms", command=self.submit
        )
        self.submit_button.pack(pady=20)

    def submit(self):
        selected_days = [day for day, var in self.day_vars.items() if var.get()]
        selected_rooms = [room for room, var in self.room_vars.items() if var.get()]
        selected_blocks = [block for block, var in self.block_vars.items() if var.get()]

        # Here you would call find_unoccupied_rooms with the selected options
        # For now, let's just print the selections
        print("Selected Days:", selected_days)
        print("Selected Rooms:", selected_rooms)
        print("Selected Time Blocks:", selected_blocks)

        # TODO: Call find_unoccupied_rooms with these selections
        # result = find_unoccupied_rooms(selected_days, selected_rooms, selected_blocks)
        # Display result (you might want to create a new window or text area for this)


if __name__ == "__main__":
    root = tk.Tk()
    gui = RoomSearchGUI(root)
    root.mainloop()
