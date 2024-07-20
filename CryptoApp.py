#import libraries needed
import requests
import sqlite3
import matplotlib
import tkinter as tk
from tkinter import font as tkfont
from tkinter import simpledialog, messagebox, ttk

class LoginDialog(simpledialog.Dialog):
    """defines custom login dialogue"""
    def body(self, master):
        """creates login form, getting user to enter username and password"""
        tk.Label(master, text="Username:").grid(row=0, column=0, sticky="e")
        tk.Label(master, text="Password:").grid(row=1, column=0, sticky="e")

        self.username_entry = tk.Entry(master)
        self.password_entry = tk.Entry(master, show="*")

        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        return self.username_entry

    def apply(self):
        "form submission"
        self.result = (self.username_entry.get(), self.password_entry.get())


class CryptoTrackerApp(tk.Tk):
    """main application class"""
    def __init__(self):
        super().__init__()
        self.title("Crypto Price Tracker")
        self.geometry("800x600")
        self.minsize(700, 500)
        self.configure(bg="#607D8B")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #initialises page stack
        self.__pages_stack = []

        #shows login page when program ran
        self.show_login_page()

    #methods to show different pages, when respective buttons pressed (and adds to stack)
    def show_login_page(self):
        login_page = LoginPage(self)
        login_page.grid(row=0, column=0, sticky="nsew")
        self.__pages_stack.append(login_page)
        login_page.tkraise()

    def show_home_page(self):
        home_page = HomePage(self)
        home_page.grid(row=0, column=0, sticky="nsew")
        self.__pages_stack.append(home_page)
        home_page.tkraise()

    def show_price_tracker_page(self):
        price_tracker_page = PriceTrackerPage(self)
        price_tracker_page.grid(row=0, column=0, sticky="nsew")
        self.__pages_stack.append(price_tracker_page)
        price_tracker_page.tkraise()

    
    def go_back(self):
        """removes froms stack, and goes back to previous page"""
        if len(self.__pages_stack) > 1:
            current_page = self.__pages_stack.pop()
            current_page.destroy()
            previous_page = self.__pages_stack[-1]
            previous_page.tkraise()
        else:
            self.quit()
            self.destroy()
        
    def refresh_page(self):
        #no error checking needed as stack will never be of length 0 in this case
        #destroys old page
        current_page = self.__pages_stack.pop()
        page_type = type(current_page)
        current_page.destroy()
            
        #creates new instance of same page type
        new_page = page_type(self)
        new_page.grid(row=0, column=0, sticky="nsew")
        self.__pages_stack.append(new_page)
        new_page.tkraise()


class LoginPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#607D8B")
        self.master = master
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        """creates login page buttons and widgets"""
        title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        title = tk.Label(self, text="Login Page", font=title_font, bg="#947E9E", fg="#FFFFFF", padx=10, pady=5)
        title.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        login_button = tk.Button(self, text="Login", bg="#333940", fg="#FFEB3B", font=("Arial", 14), padx=20, pady=10, command=self.login)
        login_button.grid(row=2, column=0, pady=20)

        signup_button = tk.Button(self, text="Signup", bg="#333940", fg="#FFEB3B", font=("Arial", 14), padx=20, pady=10, command=self.signup)
        signup_button.grid(row=3, column=0, pady=20)

    def login(self):
        """once button is pressed, this method is called. Logs user in"""
        dialog = LoginDialog(self, title="Login")
        if dialog.result:
            username, password = dialog.result
            #console output
            #print(f"Login attempted with username: {username} and password: {'*' * len(password)}")
            # TODO implement login verification
            self.master.show_home_page()

    def signup(self):
        """allows user to make account. Called when button pressed"""
        #TODO add ability to make new accounts
        messagebox.showinfo("Signup", "Signup functionality not implemented yet.")


class HomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#607D8B")
        self.master = master

        self.grid_columnconfigure(0, weight=1, minsize=150)
        self.grid_columnconfigure(1, weight=2, minsize=200)
        self.grid_rowconfigure(1, weight=1)

        self.create_widgets()

    def create_widgets(self):
        title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        title = tk.Label(self, text="Home Page", font=title_font, bg="#947E9E", fg="#FFFFFF", padx=10, pady=5)
        title.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        #left frame with nav buttons
        left_frame = tk.Frame(self, bg="#607D8B")
        left_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)

        #list of tuples of button name and command
        buttons = [
            ("Price Tracker", self.open_price_tracker),
            ("Portfolio Manager", None),
            ("Fiat Converter", None),
            ("Notes", None),
            ("Settings", None)
        ]

        for button_index, (button_text, command) in enumerate(buttons):
            button = tk.Button(left_frame, text=button_text, bg="#333940", fg="#FFEB3B", font=("Arial", 10), pady=2, wraplength=100, command=command)
            button.grid(row=button_index, column=0, pady=5, sticky="ew")

        #right frame for news
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

    def open_price_tracker(self):
        self.master.show_price_tracker_page()


class PriceTrackerPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#607D8B")
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self, text="Price Tracker", font=("Arial", 24), bg="#947E9E", fg="white", padx=10, pady=5)
        title_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        #button frame for other buttons
        buttons_frame = tk.Frame(self, bg="#607D8B")
        buttons_frame.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

        #in each tuple: button_name, command
        other_buttons = [
            ("Compare", None),
            ("Wishlist", None),
            ("See More", None),
            ("Add Coin", None)
        ]
        for index, (text, command) in enumerate(other_buttons):
            btn = tk.Button(buttons_frame, text=text, bg="#333940", fg="#FFEB3B", 
                            font=("Arial", 13), padx=11, pady=6, width=9, command=command)
            btn.grid(row=0, column=index, padx=2, pady=5)

        #back and refresh button frame
        back_refresh_frame = tk.Frame(self, bg="#607D8B")
        back_refresh_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        #back and refresh buttons
        back_btn = tk.Button(back_refresh_frame, text="Back", bg="#333940", fg="#FFEB3B", 
                             font=("Arial", 10), padx=8, pady=4, width=8, command=self.go_back)
        back_btn.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        refresh_btn = tk.Button(back_refresh_frame, text="Refresh", bg="#333940", fg="#FFEB3B", 
                                font=("Arial", 10), padx=8, pady=4, width=8, command=self.refresh_data)
        refresh_btn.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="w")

        #top coins section
        top_coins_frame = tk.Frame(self, bg="#333940", padx=10, pady=10)
        top_coins_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        top_coins_label = tk.Label(top_coins_frame, text="Top Coins", font=("Arial", 18), bg="#333940", fg="#FFEB3B")
        top_coins_label.pack(pady=(0, 10))

        #headers for the coin list (TODO edit later)
        coin_list = ttk.Treeview(top_coins_frame, columns=("Rank", "Name", "Price", "24h Change"), show="headings", height=10)
        coin_list.heading("Rank", text="Rank")
        coin_list.heading("Name", text="Name")
        coin_list.heading("Price", text="Price")
        coin_list.heading("24h Change", text="24h Change")
        coin_list.pack(fill=tk.BOTH, expand=True)

        #configures grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def go_back(self):
        self.master.go_back()

    def refresh_data(self):
        self.master.refresh_page()
        #can remove this message box later - once ik it works
        messagebox.showinfo("Refresh", "Refresh Successful")

    def update_coin_list(self, coins_data):
        """updates coin list with real data from APIs"""
        #TODO implement this once APIs working
        ...

#runs application
if __name__ == "__main__":
    app = CryptoTrackerApp()
    app.mainloop()