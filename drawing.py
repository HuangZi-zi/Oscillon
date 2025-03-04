import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageDraw

from write import BackgroundClicker


class DrawingBoard:
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

        self.color = "black"

        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.old_x = None
        self.old_y = None

        self.image = Image.new("RGB", (screen_width, screen_height - button_height), "white")
        self.draw_image = ImageDraw.Draw(self.image)

        self.root.bind("<Escape>", self.exit_program)

    def draw(self, event):
        if event.y < self.canvas.winfo_height():  # Prevent drawing on button area
            if self.old_x and self.old_y:
                self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, fill=self.color, width=3)
                self.draw_image.line([self.old_x, self.old_y, event.x, event.y], fill=self.color, width=3)
            self.old_x = event.x
            self.old_y = event.y

    def reset(self, event):
        self.old_x = None
        self.old_y = None

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.root.winfo_screenwidth(), self.root.winfo_screenheight() - 100), "white")
        self.draw_image = ImageDraw.Draw(self.image)

    def save_canvas(self):
        self.image.save("aaaaaaaaaaa.png")
        self.clear_canvas()

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