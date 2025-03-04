import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageDraw
import pyautogui
import time
import threading
import pygetwindow as gw
from pywinauto import Application
import win32gui
import win32api
import win32con

class BackgroundClicker:
    """Handles background clicking and screen overlay."""

    def __init__(self, root):
        self.root = root

    def start_clicks(self, points, callback):
        """Runs multiple clicks in a sequence and calls callback when done."""
        thread = threading.Thread(target=self.perform_clicks, args=(points, callback))
        thread.start()

    def perform_clicks(self, exe_name, points):
        """Perform background clicks in a window without bringing it to the foreground."""
        hWnd = get_window_handle_by_exe(exe_name)

        if not hWnd:
            print("Window not found!")
            return

        print(f"Clicking in window: {exe_name} (Handle: {hWnd})")
        for i, (x, y) in enumerate(points):
            print(f"Clicking at: {x}, {y} in background")
            window_click(hWnd, x, y)
            if i ==4:
                time.sleep(3)
            else:
                time.sleep(0.5)

            print("All background clicks completed.")


def get_window_handle_by_exe(exe_name):
    """Find the window handle of an application using its EXE name."""
    windows = gw.getWindowsWithTitle("")  # Get all open windows
    for win in windows:
        if exe_name.lower() in win.title.lower():  # Match by EXE name in window title
            return win._hWnd  # Return the window handle (hWnd)
    return None


def window_click(hWnd, x, y):
    """Send a background click event to a specific window at (x, y)."""
    # win32gui.SetForegroundWindow(hWnd)
    win32gui.ShowWindow(hWnd, win32con.SW_SHOWNOACTIVATE)  # Show without focus
    # win32gui.ShowWindow(hWnd, win32con.SW_MAXIMIZE)
    time.sleep(0.1)

    # relative_x, relative_y = get_relative_coords(hWnd, x, y)

    # Convert (x, y) to LPARAM format
    # lParam = win32api.MAKELONG(relative_x, relative_y)
    lParam = win32api.MAKELONG(x, y)

    # Send mouse down and mouse up messages (click simulation)
    # win32api.SetCursorPos([relative_x,relative_y])
    win32api.SendMessage(hWnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
    win32api.SendMessage(hWnd, win32con.WM_LBUTTONDOWN, 0, lParam)
    time.sleep(0.1)
    win32api.SendMessage(hWnd, win32con.WM_LBUTTONUP, 0, lParam)

def get_relative_coords(hWnd, x, y):
    left, top, right, bottom = win32gui.GetWindowRect(hWnd)  # Get window position
    return x - left, y - top  # Convert to relative coordinates

class DrawingBoard:
    """Main drawing application."""

    def __init__(self, root):
        self.root = root
        self.root.title("Drawing Board")
        # self.root.attributes('-fullscreen', True)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        button_height = 100  # Height for button area

        self.button_frame = tk.Frame(self.root, height=button_height, bg="lightgray")
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.clear_button = tk.Button(self.button_frame, text="Clear", command=self.clear_canvas, font=("Arial", 20),
                                      height=2, width=10)
        self.clear_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_canvas, font=("Arial", 20),
                                     height=2, width=10)
        self.save_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.canvas = tk.Canvas(self.root, bg="white", width=screen_width, height=screen_height - button_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.old_x = None
        self.old_y = None

        self.image = Image.new("RGB", (screen_width, screen_height - button_height), "white")
        self.draw_image = ImageDraw.Draw(self.image)

        self.clicker = BackgroundClicker(self.root)  # Create BackgroundClicker instance

        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        self.root.bind("<Escape>", self.exit_program)

        # Create a fullscreen overlay
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.configure(bg="black")
        self.overlay.withdraw()  # Start hidden

        # Loading label
        self.loading_label = tk.Label(self.overlay, text="Uploading...", font=("Arial", 30), fg="white", bg="black")
        self.loading_label.pack(expand=True)

    def draw(self, event):
        """Handles drawing when the left mouse button is held down."""
        if event.y < self.canvas.winfo_height():  # Prevent drawing on button area
            if self.old_x and self.old_y:
                self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, fill="black", width=3)
                self.draw_image.line([self.old_x, self.old_y, event.x, event.y], fill="black", width=3)
            self.old_x = event.x
            self.old_y = event.y

    def reset(self, event):
        """Resets the drawing reference points after lifting the mouse button."""
        self.old_x = None
        self.old_y = None

    def clear_canvas(self):
        """Clears the drawing canvas."""
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.root.winfo_screenwidth(), self.root.winfo_screenheight() - 100), "white")
        self.draw_image = ImageDraw.Draw(self.image)

    def save_canvas(self):
        """Saves the drawing, shows blank screen, performs clicks in the background, then restores."""
        self.image.save("aaaaaaaaaaa.png")
        self.clear_canvas()

        # Show uploading animation before hiding canvas
        self.overlay.deiconify()
        self.root.update()

        # Step 3: Click in the background (run in a separate thread)
        points = [(60, 60), (60, 105), (680, 480), (1190, 790), (100, 260), (1610, 930)]

        # target_window = "hebiglol.exe"
        # target_window = "Grbl"
        target_window = "oscillon"
        self.clicker.perform_clicks(target_window, points)

        self.overlay.withdraw()

    def exit_program(self, event):
        password = simpledialog.askstring("Exit", "Enter password to exit:", show='*')
        if password == "secure123":
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Incorrect password")


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingBoard(root)
    root.mainloop()
