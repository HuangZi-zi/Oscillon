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
import cv2

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

        self.eraser_button = tk.Button(self.button_frame, text="Eraser", command=self.toggle_eraser, font=("Arial", 20),
                                       height=2, width=10)
        self.eraser_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_canvas, font=("Arial", 20),
                                     height=2, width=10)
        self.save_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.canvas = tk.Canvas(self.root, bg="white", width=screen_width, height=screen_height - button_height)
        self.canvas.pack(fill=tk.BOTH, expand=False)

        self.old_x = None
        self.old_y = None
        self.eraser_active = False  # New variable to track eraser state

        self.image = Image.new("RGB", (screen_width, screen_height - button_height), "white")
        self.draw_image = ImageDraw.Draw(self.image)

        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.root.bind("<Escape>", self.exit_program)

        self.click_manage = ClickThrough()

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

        # Idle detection timer
        self.last_activity_time = time.time()
        self.idle_time_limit = 120  # 2 minutes
        self.video_thread = None
        self.running = True

        # Start idle detection in a separate thread
        threading.Thread(target=self.detect_idle, daemon=True).start()

    def draw(self, event):
        """Handles drawing or erasing when the left mouse button is held down."""
        if event.y < self.canvas.winfo_height():  # Prevent drawing on button area
            if self.old_x and self.old_y:
                color = "white" if self.eraser_active else "black"  # Set color based on eraser state
                width = 15 if self.eraser_active else 3  # Eraser should be wider

                self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, fill=color, width=width)
                self.draw_image.line([self.old_x, self.old_y, event.x, event.y], fill=color, width=width)

            self.old_x = event.x
            self.old_y = event.y
        self.reset_idle_timer()

    def reset(self, event):
        """Resets the drawing reference points after lifting the mouse button."""
        self.old_x = None
        self.old_y = None
        self.reset_idle_timer()

    def clear_canvas(self):
        """Clears the drawing canvas."""
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.root.winfo_screenwidth(), self.root.winfo_screenheight() - 100), "white")
        self.draw_image = ImageDraw.Draw(self.image)
        self.reset_idle_timer()

    def toggle_eraser(self):
        """Toggles the eraser on and off."""
        self.eraser_active = not self.eraser_active
        button_text = "Pen" if self.eraser_active else "Eraser"
        self.eraser_button.config(text=button_text)
        self.reset_idle_timer()

    def save_canvas(self):
        """Saves the drawing, shows blank screen, performs clicks in the background, then restores."""
        self.image = self.image.resize((1440, 825))
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
            self.click_manage.setThrouOFF()
            self.overlay.withdraw()

        threading.Thread(target=perform_clicks, daemon=True).start()
        self.reset_idle_timer()

    def reset_idle_timer(self):
        """Resets idle timer when user interacts."""
        self.last_activity_time = time.time()

    def detect_idle(self):
        """Monitors user activity and plays video after 2 minutes of inactivity."""
        while self.running:
            time.sleep(5)
            if time.time() - self.last_activity_time > self.idle_time_limit:
                self.play_video()

    def play_video(self):
        """Plays the video in a fullscreen window and exits on mouse click."""
        self.root.withdraw()  # Hide main window
        cap = cv2.VideoCapture("oscilion.mp4")  # Change to your video file

        cv2.namedWindow("Video", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        clicked = [False]  # Flag to track mouse click

        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                clicked[0] = True  # Mark clicked

        cv2.setMouseCallback("Video", on_mouse)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or clicked[0]:  # Exit if video ends or user clicks
                break

            cv2.imshow("Video", frame)
            cv2.waitKey(30)

        cap.release()
        cv2.destroyAllWindows()
        self.root.deiconify()  # Show main window
        self.reset_idle_timer()  # Reset timer after video

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
