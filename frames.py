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
        self.geometry("1280x720")
        self.minsize(800, 450)
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

    def show_portfolio_overview_page(self):
        portfolio_overview_page = PortfolioOverviewPage(self)
        portfolio_overview_page.grid(row=0, column=0, sticky="nsew")
        self.__pages_stack.append(portfolio_overview_page)
        portfolio_overview_page.tkraise()

    def show_fiat_converter_page(self):
        fiat_converter_page = FiatConverterPage(self)
        fiat_converter_page.grid(row=0, column=0, sticky="nsew")
        self.__pages_stack.append(fiat_converter_page)
        fiat_converter_page.tkraise()

    def go_back(self):
        """removes froms stack, and goes back to previous page - Can exit the whole app if used from the login page"""
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
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        title = tk.Label(self, text="Login Page", font=title_font, bg="#947E9E", fg="#FFFFFF", padx=10, pady=5)
        title.grid(row=1, column=0, sticky="ew", padx=10, pady=50)

        button_style = {"bg": "#333940", "fg": "#FFEB3B", "font": ("Arial", 14), "padx": 20, "pady": 10, "width": 10}

        login_button = tk.Button(self, text="Login", command=self.login, **button_style)
        login_button.grid(row=2, column=0, pady=10)

        signup_button = tk.Button(self, text="Signup", command=self.signup, **button_style)
        signup_button.grid(row=3, column=0, pady=10)

        exit_button = tk.Button(self, text="Exit", command=self.exit_app, **button_style)
        exit_button.grid(row=4, column=0, pady=10)

    def login(self):
        """once button is pressed, this method is called. Logs user in"""
        dialog = LoginDialog(self, title="Login")
        if dialog.result:
            username, password = dialog.result
            #console output
            #print(f"Login attempted with username: {username} and password: {'*' * len(password)}")
            #TODO implement login verification
            self.master.show_home_page()

    def signup(self):
        """allows user to make account. Called when button pressed"""
        #TODO add ability to make new accounts
        messagebox.showinfo("Signup", "Signup functionality not implemented yet.")

    def exit_app(self):
        self.master.go_back()


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
            ("Portfolio Manager", self.open_portfolio_overview),
            ("Fiat Converter", self.open_fiat_converter),
            ("Notes", None),
            ("Log Out", self.log_out)
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
    
    def open_portfolio_overview(self):
        self.master.show_portfolio_overview_page()

    def open_fiat_converter(self):
        self.master.show_fiat_converter_page()

    def log_out(self):
        self.master.go_back()
        messagebox.showinfo("Log Out", "Log Out Successful")


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
        columns=("Rank", "Name", "Price", "24h Change")
        coin_list = ttk.Treeview(top_coins_frame, columns=columns, show="headings", height=10)
        for col in columns:
            coin_list.heading(col, text=col)
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


class PortfolioOverviewPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#607D8B")
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self, text="Portfolio Overview", font=("Arial", 24), bg="#947E9E", fg="white", padx=10, pady=5)
        title_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        #button frame for other buttons
        buttons_frame = tk.Frame(self, bg="#607D8B")
        buttons_frame.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

        #in each tuple: button_name, command
        other_buttons = [
            ("Graphs", None),
            ("Badges", None),
            ("Filters", None),
            ("Sort By", None)
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
        portfolio_frame = tk.Frame(self, bg="#333940", padx=10, pady=10)
        portfolio_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        portfolio_label = tk.Label(portfolio_frame, text="Portfolio", font=("Arial", 18), bg="#333940", fg="#FFEB3B")
        portfolio_label.pack(pady=(0, 10))

        #headers for the coin list (TODO edit later)
        columns=("Rank", "Name", "Price", "24h Change")
        portfolio_list = ttk.Treeview(portfolio_frame, columns=columns, show="headings", height=10)
        for col in columns:
            portfolio_list.heading(col, text=col)
        portfolio_list.pack(fill=tk.BOTH, expand=True)

        #configures grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def go_back(self):
        self.master.go_back()

    def refresh_data(self):
        self.master.refresh_page()
        #can remove this message box later - once ik it works
        messagebox.showinfo("Refresh", "Refresh Successful")


class FiatConverterPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#607D8B")
        self.master = master
        self.currency1 = "Currency 1"
        self.currency2 = "Currency 2"
        self.create_widgets()

    def create_widgets(self):
        #title and buttons at top
        top_frame = tk.Frame(self, bg="#607D8B")
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        title_frame = tk.Frame(top_frame, bg="#947E9E")
        title_frame.pack(side=tk.LEFT)

        title_label = tk.Label(title_frame, text="Fiat\nConverter", font=("Arial", 18), bg="#947E9E", fg="white", padx=10, pady=5)
        title_label.pack(side=tk.LEFT)

        back_btn = tk.Button(top_frame, text="Back", bg="#333940", fg="#FFEB3B", font=("Arial", 10), padx=10, pady=5, command=self.go_back)
        back_btn.pack(side=tk.LEFT, padx=5)

        buttons_frame = tk.Frame(top_frame, bg="#607D8B")
        buttons_frame.pack(side=tk.RIGHT)

        presets_btn = tk.Button(buttons_frame, text="Presets", bg="#333940", fg="#FFEB3B", font=("Arial", 10), padx=10, pady=5, width=12)
        presets_btn.pack(side=tk.LEFT, padx=5)

        change_pairing_btn = tk.Button(buttons_frame, text="Change\nPairing", bg="#333940", fg="#FFEB3B", font=("Arial", 10), padx=10, pady=5, width=12)
        change_pairing_btn.pack(side=tk.LEFT, padx=5)

        #dark grey frame
        content_frame = tk.Frame(self, bg="#333940")
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        #currency pair label
        self.pair_label = tk.Label(content_frame, text=f"{self.currency1} - {self.currency2}", font=("Arial", 16, "bold"), bg="#333940", fg="#FFEB3B")
        self.pair_label.pack(pady=(20, 10))

        #white content area with dark grey border
        white_area = tk.Frame(content_frame, bg="white", highlightbackground="#333940", highlightthickness=5)
        white_area.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        #conversion ratio
        ratio_label = tk.Label(white_area, text="Ratio 1:X", font=("Arial", 12), bg="#4682B4", fg="white", padx=5, pady=2)
        ratio_label.pack(pady=(20, 10))

        #conversion frame
        conversion_frame = tk.Frame(white_area, bg="white")
        conversion_frame.pack(pady=20)

        #input to convert
        input_frame = tk.Frame(conversion_frame, bg="#4682B4", padx=10, pady=10)
        input_frame.grid(row=0, column=0, padx=5)
        
        input_label = tk.Label(input_frame, text="Enter Amount", bg="#4682B4", fg="white", font=("Arial", 12))
        input_label.pack()
        
        self.input_entry = tk.Entry(input_frame, font=("Arial", 12), width=15)
        self.input_entry.pack(pady=(5, 0))

        #equal sign
        equal_label = tk.Label(conversion_frame, text="=", font=("Arial", 16, "bold"), bg="white", fg="black")
        equal_label.grid(row=0, column=1, padx=10)

        #output after conversion
        output_frame = tk.Frame(conversion_frame, bg="#4682B4", padx=10, pady=10)
        output_frame.grid(row=0, column=2, padx=5)
        
        result_label = tk.Label(output_frame, text="Result", bg="#4682B4", fg="white", font=("Arial", 12))
        result_label.pack()
        
        self.output_entry = tk.Entry(output_frame, font=("Arial", 12), width=15, state="readonly")
        self.output_entry.pack(pady=(5, 0))

        #currency labels and swap button
        currency_frame = tk.Frame(white_area, bg="white")
        currency_frame.pack(pady=10)

        self.currency1_btn = tk.Button(currency_frame, text=self.currency1, bg="#4682B4", fg="white", font=("Arial", 12), width=10)
        self.currency1_btn.grid(row=0, column=0, padx=5)

        swap_btn = tk.Button(currency_frame, text="Swap", bg="#4682B4", fg="white", font=("Arial", 12), width=10)
        swap_btn.grid(row=0, column=1, padx=5)

        self.currency2_btn = tk.Button(currency_frame, text=self.currency2, bg="#4682B4", fg="white", font=("Arial", 12), width=10)
        self.currency2_btn.grid(row=0, column=2, padx=5)

    def go_back(self):
        self.master.go_back()

    def update_currencies(self, currency1, currency2):
        """Updates the currencies chosen to relfect new ones"""
        #TODO add functionality
        # self.currency1 = currency1
        # self.currency2 = currency2
        # self.pair_label.config(text=f"{self.currency1} - {self.currency2}")
        # self.currency1_btn.config(text=self.currency1)
        # self.currency2_btn.config(text=self.currency2)


if __name__ == "__main__":
    app = CryptoTrackerApp()
    app.mainloop()


