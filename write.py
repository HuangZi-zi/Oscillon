import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageDraw
import pyautogui
import time
import threading
import pygetwindow as gw

from win32api import SetWindowLong,RGB
from win32con import WS_EX_LAYERED,WS_EX_TRANSPARENT,GWL_EXSTYLE,LWA_ALPHA
from win32gui import GetWindowLong,GetForegroundWindow,SetLayeredWindowAttributes

import ctypes


class ClickThrough:
    Status = False
    hWindow = None
    is_working = False
    wnd_hd_list = []

    # set the window to be able to click through
    def setThrouON(self):
        # hWindow = GetForegroundWindow()
        FindWindow = ctypes.windll.user32.FindWindowW
        hwnd = FindWindow(None, "transition")
        self.wnd_hd_list.append(hwnd)
        exStyle = WS_EX_LAYERED | WS_EX_TRANSPARENT
        SetWindowLong(hwnd, GWL_EXSTYLE, exStyle)
        SetLayeredWindowAttributes(hwnd, RGB(0, 0, 0), 254, LWA_ALPHA)

    # set the window to not be click through
    def setThrouOFF(self):
        # hWindow = GetForegroundWindow()
        # SetWindowLong(hWindow, GWL_EXSTYLE,786704)
        for hWindow in set(self.wnd_hd_list):
            SetWindowLong(hWindow, GWL_EXSTYLE,256)


class DrawingBoard:
    """Main drawing application."""

    def __init__(self, root):
        self.root = root
        self.root.title("Drawing Board")
        self.root.attributes('-fullscreen', True)

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

        self.click_manage = ClickThrough()
        # self.clicker = BackgroundClicker(self.root)  # Create BackgroundClicker instance

        # **Fixed: Bind drawing events**
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.root.bind("<Escape>", self.exit_program)

        # Create a fullscreen overlay
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-topmost', 1)
        self.overlay.title('transition')
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

    import threading
    import pygetwindow as gw
    import pyautogui
    import time

    def save_canvas(self):
        """Saves the drawing, shows blank screen, performs clicks in the background, then restores."""
        self.image.save("aaaaaaaaaaa.png")
        self.clear_canvas()

        # Step 1: Show overlay (transition animation)
        self.overlay.deiconify()  # Show blank overlay
        self.root.update()

        # Step 2: Minimize all "Drawing Board" windows
        drawing_windows = gw.getWindowsWithTitle("Drawing Board")
        # drawing_windows[0].activate()  # Bring it to the front

        drawing_windows[0].minimize()
        self.click_manage.setThrouON()
        # for window in drawing_windows:
        #     window.minimize()
        time.sleep(1)  # Give time to minimize

        # Step 3: Click in the background (run in a separate thread)
        def perform_clicks():
            points = [(60, 60), (60, 105), (680, 480), (1190, 790), (100, 260), (1610, 920)]
            i = 0
            for x, y in points:
                pyautogui.moveTo(x, y, duration=0.5)  # Move cursor to location smoothly
                pyautogui.click()
                if i == 4:
                    time.sleep(3)  # Adjust delay as needed
                else:
                    time.sleep(0.5)
                i += 1

            # Step 4: Restore all "Drawing Board" windows after clicking
            for window in drawing_windows:
                window.restore()
                time.sleep(1)  # Wait for the app to restore
                window.activate()  # Bring it to the front

            # Hide overlay after clicking
            self.overlay.withdraw()
            self.click_manage.setThrouOFF()

        threading.Thread(target=perform_clicks, daemon=True).start()

    def exit_program(self, event):
        password = simpledialog.askstring("Exit", "Enter password to exit:", show='*')
        if password == "secure123":
            self.click_manage.setThrouOFF()
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Incorrect password")


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingBoard(root)
    root.mainloop()
    app.click_manage.setThrouOFF()
