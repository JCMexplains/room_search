#!/usr/bin/env python3
"""
Room Finder Application
-----------------------
A tool to find vacant rooms on campus.
"""

import sys
import tkinter as tk

from src.gui.simple_gui import RoomFinderGUI


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = RoomFinderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
