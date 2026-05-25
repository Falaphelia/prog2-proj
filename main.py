"""
Main application execution module.
Is responsible for launching the GUI, and also switching between fullscreen.
"""

import tkinter as tk
import game.gui.app as gui

def toggle_fullscreen(e):
    """
    When called, toggles the fullscreen state of the tk GUI.
    """
    if root.attributes('-fullscreen'):
        root.attributes('-fullscreen', False)

    else:
        root.attributes('-fullscreen', True)

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.iconbitmap("assets/icon.ico")
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    root.bind("<F11>", toggle_fullscreen)
    gui_instance = gui.GameGUI(root)
    root.tk.mainloop()
