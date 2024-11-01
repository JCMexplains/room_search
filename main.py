from src.gui.simple_gui import RoomFinderGUI
import tkinter as tk

def main():
    root = tk.Tk()
    app = RoomFinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
