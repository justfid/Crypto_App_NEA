#import libraries needed
import requests
import sqlite3
import matplotlib
import tkinter as tk
from tkinter import font as tkfont
from tkinter import simpledialog, messagebox

#defines custom login dialogue
class LoginDialog(simpledialog.Dialog):
    #creates login form
    def body(self, master):
        #enter username and password
        tk.Label(master, text="Username:").grid(row=0, column=0, sticky="e")
        tk.Label(master, text="Password:").grid(row=1, column=0, sticky="e")

        self.username_entry = tk.Entry(master)
        self.password_entry = tk.Entry(master, show="*")

        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        return self.username_entry

    #form submission
    def apply(self):
        self.result = (self.username_entry.get(), self.password_entry.get())

#main application class
class CryptoTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto Price Tracker")
        self.geometry("600x400")
        self.minsize(400, 300)
        self.configure(bg="#607D8B")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #shows login page when ran
        self.show_login_page()

    #method to display login page
    def show_login_page(self):
        self.login_page = LoginPage(self)
        self.login_page.grid(row=0, column=0, sticky="nsew")

    #method to display home page
    def show_home_page(self):
        self.login_page.destroy()
        self.home_page = HomePage(self)
        self.home_page.grid(row=0, column=0, sticky="nsew")

#login page
class LoginPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#607D8B")
        self.master = master
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    #creates login page widgets
    def create_widgets(self):
        #creates buttons
        title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        title = tk.Label(self, text="Login Page", font=title_font, bg="#947E9E", fg="#FFFFFF", padx=10, pady=5)
        title.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        login_button = tk.Button(self, text="Login", bg="#333940", fg="#FFEB3B", font=("Arial", 14), padx=20, pady=10, command=self.login)
        login_button.grid(row=2, column=0, pady=20)

        signup_button = tk.Button(self, text="Signup", bg="#333940", fg="#FFEB3B", font=("Arial", 14), padx=20, pady=10, command=self.signup)
        signup_button.grid(row=3, column=0, pady=20)

    #after clicking login button
    def login(self):
        dialog = LoginDialog(self, title="Login")
        if dialog.result:
            username, password = dialog.result
            #console output
            #print(f"Login attempted with username: {username} and password: {'*' * len(password)}")
            # TODO implement login verification
            self.master.show_home_page()

    #after clicking signup button
    def signup(self):
        # TODO add ability to make new accounts
        messagebox.showinfo("Signup", "Signup functionality not implemented yet.")

#home page
class HomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#607D8B")
        self.master = master

        self.grid_columnconfigure(0, weight=1, minsize=150)
        self.grid_columnconfigure(1, weight=2, minsize=200)
        self.grid_rowconfigure(1, weight=1)

        self.create_widgets()

    #creates home page widgets
    def create_widgets(self):
        #creates title
        title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        title = tk.Label(self, text="Home Page", font=title_font, bg="#947E9E", fg="#FFFFFF", padx=10, pady=5)
        title.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        #creates left frame with nav buttons
        left_frame = tk.Frame(self, bg="#607D8B")
        left_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)

        buttons = ["Price Tracker", "Portfolio Manager", "Fiat Converter", "Notes", "Settings"]

        for button_index, button_text in enumerate(buttons):
            button = tk.Button(left_frame, text=button_text, bg="#333940", fg="#FFEB3B", font=("Arial", 10), pady=2, wraplength=100)
            button.grid(row=button_index, column=0, pady=5, sticky="ew")

        #creates right frame for news
        right_frame = tk.Frame(self, bg="#333940")
        right_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        news_label = tk.Label(right_frame, text="News", bg="#333940", fg="#FFEB3B", font=("Arial", 12, "bold"))
        news_label.grid(row=0, column=0, pady=5, sticky="ew")

        news_text = tk.Text(right_frame, bg="#FFFFFF", fg="#333940", font=("Arial", 9), wrap=tk.WORD)
        news_text.insert("1.0", "[News headlines added here - clickable]")
        news_text.config(state="disabled")
        news_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

#runs application
if __name__ == "__main__":
    app = CryptoTrackerApp()
    app.mainloop()