import tkinter as tk
from tkinter import font as tkfont
import requests
import sqlite3
import matplotlib

class CryptoTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Crypto Price Tracker")
        self.geometry("600x400")
        self.minsize(400, 300)  # Set minimum window size
        self.configure(bg="#607D8B")  # Blueish Grey background

        self.grid_columnconfigure(0, weight=1, minsize=150)
        self.grid_columnconfigure(1, weight=2, minsize=200)
        self.grid_rowconfigure(1, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        title = tk.Label(self, text="Home Page", font=title_font, bg="#947E9E", fg="#FFFFFF", padx=10, pady=5)
        title.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Left frame for buttons
        left_frame = tk.Frame(self, bg="#607D8B")
        left_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)

        buttons = [
            "Price Tracker",
            "Portfolio Manager",
            "Fiat Converter",
            "Notes",
            "Settings"
        ]

        for i, button_text in enumerate(buttons):
            button = tk.Button(left_frame, text=button_text, bg="#333940", fg="#FFEB3B", 
                               font=("Arial", 10), pady=2, wraplength=100)
            button.grid(row=i, column=0, pady=5, sticky="ew")

        # Right frame for news
        right_frame = tk.Frame(self, bg="#333940")
        right_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        news_label = tk.Label(right_frame, text="News", bg="#333940", fg="#FFEB3B", font=("Arial", 12, "bold"))
        news_label.grid(row=0, column=0, pady=5, sticky="ew")

        news_text = tk.Text(right_frame, bg="#FFFFFF", fg="#333940", font=("Arial", 9), wrap=tk.WORD)
        news_text.insert("1.0", "[News headlines added here - clickable]")
        news_text.config(state="disabled")  # Make it read-only
        news_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    def on_resize(self, event):
        # Adjust font sizes based on window width
        window_width = event.width
        if window_width < 500:
            self.adjust_fonts(small=True)
        else:
            self.adjust_fonts(small=False)

    def adjust_fonts(self, small=False):
        for widget in self.winfo_children() + self.winfo_children()[1].winfo_children():
            if isinstance(widget, tk.Button):
                font_size = 8 if small else 10
                widget.config(font=("Arial", font_size))
            elif isinstance(widget, tk.Label) and widget.cget("text") == "Home Page":
                font_size = 14 if small else 16
                widget.config(font=("Arial", font_size, "bold"))
            elif isinstance(widget, tk.Label) and widget.cget("text") == "News":
                font_size = 10 if small else 12
                widget.config(font=("Arial", font_size, "bold"))

if __name__ == "__main__":
    app = CryptoTrackerApp()
    app.bind("<Configure>", app.on_resize)
    app.mainloop()