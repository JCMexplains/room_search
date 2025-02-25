import sys
import tkinter as tk
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.gui.simple_gui import RoomFinderGUI


def main():
    root = tk.Tk()
    app = RoomFinderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
