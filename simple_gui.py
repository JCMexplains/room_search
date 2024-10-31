import tkinter as tk
from tkinter import ttk
import pandas as pd
from room_finder import find_vacant_rooms

def get_valid_terms(data_file: str = "data.csv") -> list[int]:
    """Get list of valid terms from the CSV file"""
    df = pd.read_csv(f"data/{data_file}")
    return sorted(df['term'].unique().tolist())

class RoomFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Room Finder")
        
        # Get valid terms from CSV
        self.valid_terms = get_valid_terms()
        self.valid_sessions = [1, 2, 3, 4]
        
        # Term/Session Frame
        frame = ttk.LabelFrame(root, text="Term & Session", padding=10)
        frame.pack(fill="x", padx=5, pady=5)
        
        # Term Dropdown
        ttk.Label(frame, text="Term:").pack(side="left")
        self.term_var = tk.StringVar(value=str(self.valid_terms[0]))
        term_dropdown = ttk.Combobox(
            frame, 
            textvariable=self.term_var,
            values=self.valid_terms,
            width=10,
            state="readonly"
        )
        term_dropdown.pack(side="left", padx=5)
        
        # Session Dropdown
        ttk.Label(frame, text="Session:").pack(side="left")
        self.session_var = tk.StringVar(value="1")
        session_dropdown = ttk.Combobox(
            frame, 
            textvariable=self.session_var,
            values=self.valid_sessions,
            width=5,
            state="readonly"
        )
        session_dropdown.pack(side="left", padx=5)
        
        # Days Frame
        days_frame = ttk.LabelFrame(root, text="Days", padding=10)
        days_frame.pack(fill="x", padx=5, pady=5)
        
        self.day_vars = {}
        for day in "MTWRFS":
            self.day_vars[day] = tk.BooleanVar(value=True)
            ttk.Checkbutton(days_frame, text=day, variable=self.day_vars[day]).pack(side="left")
        
        # Search Button
        ttk.Button(root, text="Find Vacant Rooms", command=self.search).pack(pady=10)
        
        # Results
        self.results = tk.Text(root, height=20, width=60)
        self.results.pack(padx=5, pady=5, fill="both", expand=True)
    
    def search(self):
        term = int(self.term_var.get())
        session = int(self.session_var.get())
        days = [day for day, var in self.day_vars.items() if var.get()]
        
        vacancies = find_vacant_rooms(term, session, days)
        
        # Display results
        self.results.delete(1.0, tk.END)
        for room, days in vacancies.items():
            self.results.insert(tk.END, f"\nBuilding {room[0]}, Room {room[1]}:\n")
            for day, blocks in days.items():
                if blocks:
                    times = [f"{block[0].strftime('%H:%M')}-{block[1].strftime('%H:%M')}" 
                            for block in blocks]
                    self.results.insert(tk.END, f"{day}: {', '.join(times)}\n")

def main():
    root = tk.Tk()
    app = RoomFinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 