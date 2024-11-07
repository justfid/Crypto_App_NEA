import tkinter as tk
from tkinter import font as tkfont
from tkinter import simpledialog, messagebox, ttk
from apifunctions import get_price_tracker_data, get_exchange_rate, get_formatted_news, get_coin_ticker_with_key
from mathfunctions import round_to_sf, merge_sort
from sqlcode import (add_new_user, check_username_exists, add_coin_to_list, 
                    remove_coin_from_list, add_transaction_to_db, add_coin_to_database, 
                    fetch_transactions, save_note_to_db, delete_note_from_db, 
                    update_note_title_in_db, get_notes_list, get_note_content)
from utils import verify_password, get_top_coins
import webbrowser
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
        self.title("Crypto Analysis App")
        self.geometry("1920x1080")
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

    def show_notes_page(self):
        notes_page = NotesPage(self)
        notes_page.grid(row=0, column=0, sticky="nsew")
        self.__pages_stack.append(notes_page)
        notes_page.tkraise()

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
        """called once button is pressed. Logs user in"""
        dialog = LoginDialog(self, title="Login")
        if dialog.result:
            username, password = dialog.result
            if not username or not password:
                messagebox.showerror("Error", "Either Username or Password is Blank. Try again")
            else:  
                if check_username_exists(username) and verify_password(password, username):
                    global logged_in_user 
                    logged_in_user = username
                    self.master.show_home_page()
                else:
                    messagebox.showerror("Error", "Incorrect Username or Password")
            
    def signup(self):
        """creates account"""
        dialog = LoginDialog(self, title="Signup")
        if dialog.result:
            username, password = dialog.result
            #if one blank
            if not username or not password:
                messagebox.showerror("Error", "Either Username or Password is Blank. Try again")
            else:
                success = add_new_user(username, password)
                if success:
                    self.add_default_coins(username)
                    messagebox.showinfo("Success", "New Account Created")
                else:
                    messagebox.showerror("Error", "Username Already Exists. Try Again")
    
    def add_default_coins(self, username):
        for name in ["bitcoin","ethereum"]:
            add_coin_to_list(username, name)

    def exit_app(self):
        self.master.go_back()


class HomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#607D8B")
        self.master = master

        self.grid_columnconfigure(0, weight=1, minsize=150)
        self.grid_columnconfigure(1, weight=2, minsize=200)
        self.grid_rowconfigure(1, weight=1)

        self.news_page = 1
        self.previous_news = None

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
            ("Notes", self.open_notes),
            ("Get More News", self.get_more_news),
            ("Log Out", self.log_out),
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

        #ceates treeview with 3 columns
        self.news_tree = ttk.Treeview(right_frame, columns=("title", "ticker", "date"), show="headings")
        self.news_tree.heading("title", text="Title")
        self.news_tree.heading("ticker", text="Ticker")
        self.news_tree.heading("date", text="Date / Time Published")
        self.news_tree.column("title", anchor=tk.W, width=200)
        self.news_tree.column("ticker", anchor=tk.CENTER, width=100)
        self.news_tree.column("date", anchor=tk.CENTER, width=100)
        self.news_tree.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        #scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.news_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.news_tree.configure(yscrollcommand=scrollbar.set)

        #binds double-click event
        self.news_tree.bind("<Double-1>", self.on_news_click)
        self.get_more_news()

    def get_more_news(self):
        news_stories = get_formatted_news(f"&page={self.news_page}")
        if self.previous_news == news_stories:
            self.news_tree.insert("", "end", values=("END OF STORIES", "N/A", "N/A"), tags=("END"))
            self.previous_news = "END"
            messagebox.showinfo("End of Stories", "All available stories have been shown")
        elif self.previous_news == "END":
            messagebox.showinfo("End of Stories", "All available stories have been shown")
        else:
            for story in news_stories:
                title, ticker, date, link = story["title"], story["ticker"], story["published_at"], story["url"]
                self.news_tree.insert("", "end", values=(title, ticker, date), tags=(link))
            self.previous_news = news_stories
            self.news_page += 1

    def on_news_click(self, event):
        item = self.news_tree.selection()[0]
        link = self.news_tree.item(item, "tags")[0]
        if link == "END":
            pass
        else: 
            webbrowser.open_new(link)

    def open_price_tracker(self):
        self.master.show_price_tracker_page()
    
    def open_portfolio_overview(self):
        self.master.show_portfolio_overview_page()

    def open_fiat_converter(self):
        self.master.show_fiat_converter_page()

    def open_notes(self):
        self.master.show_notes_page()

    def log_out(self):
        self.master.go_back()
        global logged_in_user
        logged_in_user = None
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
            ("Add Coin", self.add_coin),
            ("Remove Coin", self.remove_coin),
            ("Sort By", self.sort)
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

        columns = ("Name", "Ticker", "Price (USD)", "1h Change (%)", 
                  "24h Change (%)", "7d Change (%)", "Market Cap (USD)", "Rank (Market Cap)")
        self.coin_list = ttk.Treeview(top_coins_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.coin_list.heading(col, text=col)
            if col in ["Name", "Ticker"]:
                self.coin_list.column(col, width=100, stretch=True)
            elif col in ["Price (USD)", "1h Change (%)", "24h Change (%)", "7d Change (%)"]:
                self.coin_list.column(col, width=120, stretch=True)
            else:
                self.coin_list.column(col, width=150, stretch=True)
        
        self.coin_list.pack(fill=tk.BOTH, expand=True)

        self.load_price_data()

        #configures grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def load_price_data(self):
        # Clear existing items
        for item in self.coin_list.get_children():
            self.coin_list.delete(item)
            
        coins = get_top_coins(logged_in_user)
        if len(coins) > 100:
            coins = coins[:100]

        data = get_price_tracker_data(coins)
        for x, values in data.items():
            if values:
                formatted_values = (
                    values[0],                           # Name
                    values[1].upper(),                   # Ticker
                    f"${values[2]:,.2f}",               # Price
                    f"{values[3]:.2f}%",                # 1h Change
                    f"{values[4]:.2f}%",                # 24h Change
                    f"{values[5]:.2f}%",                # 7d Change
                    f"${values[6]:,.2f}",               # Market Cap
                    values[7] if values[7] else "N/A"    # Rank
                )
                self.coin_list.insert("", 0, values=formatted_values)

    def add_coin(self):
        coin = simpledialog.askstring("Add Coin", "Enter the name of the coin:")
        if not coin:
            return
        coin = coin.strip().lower()
        
        if coin in ["ripple", "xrp"]:
            coin = "xrp"
            ticker = "rlusd"  #rlusd instead of XRP
        else:
            ticker = coin
            
        success = add_coin_to_list(logged_in_user, ticker)
        if success:
            messagebox.showinfo("Success", f"{coin.upper()} has been added to your list.")
            self.load_price_data()
        else:
            messagebox.showerror("Error", f"Failed to add {coin.upper()}. It may already be in your list or not exist in our database.")

    def remove_coin(self):
        selected_items = self.coin_list.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a coin to remove.")
            return
        
        if len(self.coin_list.get_children()) <= 1:
            messagebox.showerror("Error", "Cannot remove the last coin. Your list must contain at least one coin.")
            return
    
        item = selected_items[0]
        coin_data = self.coin_list.item(item, "values")
        coin_ticker = coin_data[1]
        
        display_ticker = coin_ticker
        db_ticker = "rlusd" if coin_ticker.lower() == "xrp" else coin_ticker
        
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove {display_ticker}?"):
            success = remove_coin_from_list(logged_in_user, db_ticker)
            if success:
                self.load_price_data()
                messagebox.showinfo("Success", f"{display_ticker} has been removed from your list.")
            else:
                messagebox.showerror("Error", f"Failed to remove {display_ticker} from your list.")

    def sort(self):
        sort_dialog = tk.Toplevel(self)
        sort_dialog.title("Sort Options")
        sort_dialog.geometry("300x150")
        sort_dialog.resizable(False, False)

        tk.Label(sort_dialog, text="Sort by:").pack(pady=5)
        
        columns = ["Name", "Ticker", "Price (USD)", "1h Change (%)", "24h Change (%)", 
                   "7d Change (%)", "Market Cap (USD)", "Rank (Market Cap)"]
        sort_column = tk.StringVar(value=columns[0])
        column_dropdown = ttk.Combobox(sort_dialog, textvariable=sort_column, values=columns, state="readonly")
        column_dropdown.pack(pady=5)

        sort_order = tk.StringVar(value="Ascending")
        tk.Radiobutton(sort_dialog, text="Ascending", variable=sort_order, value="Ascending").pack()
        tk.Radiobutton(sort_dialog, text="Descending", variable=sort_order, value="Descending").pack()

        def apply_sort():
            column = sort_column.get()
            order = sort_order.get()
            reverse = order == "Descending"
            
            data = [(self.coin_list.set(child, column), child) 
                   for child in self.coin_list.get_children('')]

            def key_function(item):
                return self.convert_value(item[0], column)

            sorted_data = merge_sort(data, key_function)

            if reverse:
                sorted_data.reverse()

            for index, (_, child) in enumerate(sorted_data):
                self.coin_list.move(child, '', index)

            sort_dialog.destroy()

        tk.Button(sort_dialog, text="Apply", command=apply_sort).pack(pady=10)
        self.wait_window(sort_dialog)

    def convert_value(self, value, column):
        if column in ["Price (USD)", "1h Change (%)", "24h Change (%)", "7d Change (%)"]:
            return float(value.strip('%$').replace(',', ''))
        elif column == "Market Cap (USD)":
            return float(value.strip('$').replace(',', ''))
        elif column == "Rank (Market Cap)":
            return float(value) if value != "N/A" else float('inf')
        else:
            return value.lower()

    def go_back(self):
        self.master.go_back()

    def refresh_data(self):
        self.load_price_data()
        messagebox.showinfo("Success","Refresh Complete")

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
            ("Add Transaction", self.add_transaction),
            ("Graphs", self.get_chart),
            ("Filters", self.filters),
            ("Sort By", self.sort)
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

        columns=("Coin", "Price", "Quantity", "Value Now", "Value When Bought", "Gain/Loss", "% Gain/Loss")
        self.portfolio_list = ttk.Treeview(portfolio_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.portfolio_list.heading(col, text=col)
        self.portfolio_list.pack(fill=tk.BOTH, expand=True)

        self.load_portfolio_data()

        #configures grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def load_portfolio_data(self):
        transactions = fetch_transactions(logged_in_user)
        
        valid_coin_ids = []
        coin_info_cache = {}
        
        for coin in transactions.keys():
            coin_id = ("bitcoin" if coin.upper() == "BTC" else 
                    "ethereum" if coin.upper() == "ETH" else 
                    "dogecoin" if coin.upper() == "DOGE" else 
                    "ripple" if coin.upper() in ["XRP","RLUSD"] else coin.lower())
            valid_coin_ids.append(coin_id)
            coin_info_cache[coin] = coin_id
                
        if not valid_coin_ids:
            messagebox.showwarning("No Data", "No valid coin data available to display.")
            return
                
        current_prices = get_price_tracker_data(valid_coin_ids)
        
        for coin, data in transactions.items():
            quantity = data['quantity']
            price_bought = data['total_value']
            
            coin_id = coin_info_cache[coin]
            coin_data = current_prices.get(coin_id, [])
            current_price = coin_data[2] if coin_data and len(coin_data) >= 3 else 0
            
            if current_price == 0:
                print(f"Warning: No price data available for {coin}")
            
            value_now = quantity * current_price
            gain_loss = value_now - price_bought
            percent_gain_loss = (gain_loss / price_bought) * 100 if price_bought != 0 else 0
            
            self.portfolio_list.insert("", "end", values=(
                coin,
                f"${current_price:.2f}",
                f"{quantity:.8f}",
                f"${value_now:.2f}",
                f"${price_bought:.2f}",
                f"${gain_loss:.2f}",
                f"{percent_gain_loss:.2f}%"
            ))

    def add_transaction(self):
        coin_id = simpledialog.askstring("Add Coin", "Enter the name of the coin:").lower()
        if not coin_id:
            messagebox.showerror("Error", "Coin cannot be empty.")
            return
        
        time.sleep(0.5)
        value = simpledialog.askfloat("Add Transaction", "Enter the transaction value:")
        if value is None or value == 0:
            messagebox.showerror("Error", "Invalid transaction value.")
            return
        value = round(float(value),2)

        try:
            coin_ticker = get_coin_ticker_with_key(coin_id)
            if not coin_ticker:
                messagebox.showerror("Error", f"{coin_id} is not a valid coin")
                return
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred while fetching coin data.\n\nError: {str(e)}")
            return
    
        
        #ensures no negative balance
        current_prices = get_price_tracker_data([coin_id]) 
        current_price = current_prices.get(coin_id, [None, None, None])[2]

        if current_price is None or current_price == 0:
            messagebox.showerror("Error", f"Unable to fetch current price for {coin_ticker} (ID: {coin_id}).")
            return
        
        quantity = value / current_price
    
        transactions = fetch_transactions(logged_in_user)
        current_quantity = transactions.get(coin_ticker, {'quantity': 0})['quantity']
        
        if value < 0 and abs(quantity) > current_quantity:
            messagebox.showerror("Error", f"Transaction would result in negative balance. Current holdings: {current_quantity:.8f}")
            return

        #adds to db if not exists in coin table
        exists = check_ticker_exists(coin_ticker)
        if not exists:
            add_coin_to_database(coin_ticker, coin_id)

        current_prices = get_price_tracker_data([coin_id]) 
        current_price = current_prices.get(coin_id, [None, None, None])[2]
    
        if current_price is None or current_price == 0:
            messagebox.showerror("Error", f"Unable to fetch current price for {coin_ticker} (ID: {coin_id}).")
            return
        
        quantity = value / current_price
        confirm_msg = f"You are about to add a transaction:\n\n" \
                    f"Coin: {coin_id}\n" \
                    f"Value: ${value:.2f}\n" \
                    f"Current Price: ${current_price:.2f}\n" \
                    f"Quantity: {quantity:.8f}\n\n" \
                    f"Do you want to proceed?"
        
        if not messagebox.askyesno("Confirm Transaction", confirm_msg):
            return

        success = add_transaction_to_db(logged_in_user, coin_ticker, value, quantity)
        if success:
            messagebox.showinfo("Success", f"Transaction added successfully. Value: ${value:.2f}, Quantity: {quantity:.8f}")
            self.refresh_data()
        else:
            messagebox.showerror("Error", "Failed to add transaction to the database.")
    
    def sort(self):
        sort_dialog = tk.Toplevel(self)
        sort_dialog.title("Sort Options")
        sort_dialog.geometry("300x150")
        sort_dialog.resizable(False, False)

        tk.Label(sort_dialog, text="Sort by:").pack(pady=5)
        
        columns = ["Coin", "Price", "Quantity", "Value Now", "Value When Bought", "Gain/Loss", "% Gain/Loss"]
        sort_column = tk.StringVar(value=columns[0])
        column_dropdown = ttk.Combobox(sort_dialog, textvariable=sort_column, values=columns, state="readonly")
        column_dropdown.pack(pady=5)

        sort_order = tk.StringVar(value="Ascending")
        tk.Radiobutton(sort_dialog, text="Ascending", variable=sort_order, value="Ascending").pack()
        tk.Radiobutton(sort_dialog, text="Descending", variable=sort_order, value="Descending").pack()

        def apply_sort():
            column = sort_column.get()
            order = sort_order.get()
            reverse = order == "Descending"
            
            #gets all items in treeview
            data = [(self.portfolio_list.set(child, column), child) for child in self.portfolio_list.get_children('')]

            #defines key function for sorting
            def key_function(item):
                return self.convert_value(item[0], column)

            #sorts data using merge sort
            sorted_data = merge_sort(data, key_function)

            #reverses if descending order
            if reverse:
                sorted_data.reverse()

            #rearranges items in sorted positions
            for index, (_, child) in enumerate(sorted_data):
                self.portfolio_list.move(child, '', index)

            sort_dialog.destroy()

        tk.Button(sort_dialog, text="Apply", command=apply_sort).pack(pady=10)

        # Wait for the dialog to be closed
        self.wait_window(sort_dialog)

    def convert_value(self, value, column):
        if column in ["Price", "Value Now", "Value When Bought", "Gain/Loss"]:
            return float(value.strip('$').replace(',', ''))
        elif column in ["Quantity", "% Gain/Loss"]:
            return float(value.strip('%'))
        else:
            return value.lower()

    def filters(self):
        filter_dialog = tk.Toplevel(self)
        filter_dialog.title("Filter Options")
        filter_dialog.geometry("400x300")
        filter_dialog.resizable(False, False)
        
        # Value filters
        tk.Label(filter_dialog, text="Value Filters", font=("Arial", 11, "bold")).pack(pady=(10,5))
        value_frame = tk.Frame(filter_dialog)
        value_frame.pack(fill="x", padx=20)
        
        tk.Label(value_frame, text="Min Value ($):").grid(row=0, column=0, padx=5)
        min_value = tk.Entry(value_frame, width=15)
        min_value.grid(row=0, column=1, padx=5)
        
        tk.Label(value_frame, text="Max Value ($):").grid(row=0, column=2, padx=5)
        max_value = tk.Entry(value_frame, width=15)
        max_value.grid(row=0, column=3, padx=5)
        
        # Gain/Loss filters
        tk.Label(filter_dialog, text="Gain/Loss Filters", font=("Arial", 11, "bold")).pack(pady=(15,5))
        gl_frame = tk.Frame(filter_dialog)
        gl_frame.pack(fill="x", padx=20)
        
        tk.Label(gl_frame, text="Min G/L (%):").grid(row=0, column=0, padx=5)
        min_gl = tk.Entry(gl_frame, width=15)
        min_gl.grid(row=0, column=1, padx=5)
        
        tk.Label(gl_frame, text="Max G/L (%):").grid(row=0, column=2, padx=5)
        max_gl = tk.Entry(gl_frame, width=15)
        max_gl.grid(row=0, column=3, padx=5)
        
        # Show/Hide options
        tk.Label(filter_dialog, text="Display Options", font=("Arial", 11, "bold")).pack(pady=(15,5))
        options_frame = tk.Frame(filter_dialog)
        options_frame.pack(pady=5)
        
        show_profit = tk.BooleanVar(value=True)
        show_loss = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="Show Profitable", variable=show_profit).pack(pady=2)
        tk.Checkbutton(options_frame, text="Show Losses", variable=show_loss).pack(pady=2)
        
        def apply_filters():
            try:
                filters = {
                    'min_value': float(min_value.get()) if min_value.get() else None,
                    'max_value': float(max_value.get()) if max_value.get() else None,
                    'min_gl': float(min_gl.get()) if min_gl.get() else None,
                    'max_gl': float(max_gl.get()) if max_gl.get() else None,
                    'show_profit': show_profit.get(),
                    'show_loss': show_loss.get()
                }
                self.apply_portfolio_filters(filters)
                filter_dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for all numeric fields")

        def reset_filters():
            # Reload all portfolio data
            self.portfolio_list.delete(*self.portfolio_list.get_children())
            self.load_portfolio_data()
            filter_dialog.destroy()

        ttk.Separator(filter_dialog, orient='horizontal').pack(fill='x', pady=15)
        
        # Button frame for both buttons
        button_frame = tk.Frame(filter_dialog)
        button_frame.pack(pady=5)
        
        tk.Button(button_frame, text="Apply", command=apply_filters).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Reset", command=reset_filters).pack(side=tk.LEFT, padx=5)

    def apply_portfolio_filters(self, filters):
        items = self.portfolio_list.get_children('')
        
        for item in items:
            values = self.portfolio_list.item(item)['values']
            try:
                current_value = float(values[3].replace('$', '').replace(',', ''))
                gl_percent = float(values[6].replace('%', ''))
                
                # Check all conditions
                if (filters['min_value'] and current_value < filters['min_value'] or
                    filters['max_value'] and current_value > filters['max_value'] or
                    filters['min_gl'] and gl_percent < filters['min_gl'] or
                    filters['max_gl'] and gl_percent > filters['max_gl'] or
                    gl_percent >= 0 and not filters['show_profit'] or
                    gl_percent < 0 and not filters['show_loss']):
                    self.portfolio_list.detach(item)
                else:
                    self.portfolio_list.reattach(item, '', 'end')
                    
            except (ValueError, IndexError):
                self.portfolio_list.reattach(item, '', 'end')
                
    def get_chart(self):
        # Create new window for graphs
        graph_window = tk.Toplevel(self)
        graph_window.title("Portfolio Analysis")
        graph_window.geometry("800x600")
        
        # Get portfolio data
        items = self.portfolio_list.get_children('')
        
        # Extract data for charts
        coins = []
        values = []
        gains = []
        
        total_value = 0
        for item in items:
            data = self.portfolio_list.item(item)['values']
            coin = data[0]
            current_value = float(data[3].replace('$', '').replace(',', ''))
            gain_loss = float(data[5].replace('$', '').replace(',', ''))
            
            coins.append(coin)
            values.append(current_value)
            gains.append(gain_loss)
            total_value += current_value

        # Calculate percentages for pie chart
        percentages = [v/total_value * 100 for v in values]

        # Create figure with subplots
        fig = Figure(figsize=(12, 5))
        
        # Pie chart for allocation
        ax1 = fig.add_subplot(121)
        wedges, texts, autotexts = ax1.pie(percentages, labels=coins, autopct='%1.1f%%')
        ax1.set_title('Portfolio Allocation')
        
        # Format pie chart text
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=8)
        
        # Bar chart for gains/losses
        ax2 = fig.add_subplot(122)
        x_positions = range(len(coins))  # Create positions for bars
        colors = ['g' if x >= 0 else 'r' for x in gains]
        ax2.bar(x_positions, gains, color=colors)
        ax2.set_title('Gains/Losses by Coin')
        
        # Properly set ticks and labels
        ax2.set_xticks(x_positions)  # Set tick positions
        ax2.set_xticklabels(coins, rotation=45)  # Set tick labels
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # Format layout
        fig.tight_layout(pad=3.0)
        
        # Create canvas and add to window
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Add total portfolio value
        total_label = tk.Label(graph_window, 
                            text=f"Total Portfolio Value: ${total_value:,.2f}",
                            font=("Arial", 12, "bold"))
        total_label.pack(pady=10)

    def go_back(self):
        self.master.go_back()

    def refresh_data(self):
        self.master.refresh_page()
    

class FiatConverterPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#607D8B")
        self.master = master
        self.currency1 = "GBP" 
        self.currency2 = "USD"
        self.amount = 0
        self.rate = get_exchange_rate(self.currency1, self.currency2)
        self.currencies = ['AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'EUR', 'GBP', 'HKD',
                           'HRK', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN', 'MYR', 'NOK', 
                           'NZD', 'PHP', 'PLN', 'RON', 'RUB', 'SEK', 'SGD', 'THB', 'TRY', 'USD', 'ZAR']
        self.create_widgets()

    def create_widgets(self):
        #title and buttons at top
        top_frame = tk.Frame(self, bg="#607D8B")
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        title_frame = tk.Frame(top_frame, bg="#947E9E")
        title_frame.pack(side=tk.LEFT)

        title_label = tk.Label(title_frame, text="Fiat Converter", font=("Arial", 18), bg="#947E9E", fg="white", padx=10, pady=5)
        title_label.pack(side=tk.LEFT)

        back_btn = tk.Button(top_frame, text="Back", bg="#333940", fg="#FFEB3B", font=("Arial", 10), padx=10, pady=5, command=self.go_back)
        back_btn.pack(side=tk.RIGHT, padx=5)

        #dark grey frame
        content_frame = tk.Frame(self, bg="#333940")
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        #currency pair label
        self.pair_label = tk.Label(content_frame, text=f"{self.currency1} - {self.currency2}", font=("Arial", 16, "bold"), bg="#333940", fg="#FFEB3B")
        self.pair_label.pack(pady=(20, 10))

        #white content area with dark grey border
        white_area = tk.Frame(content_frame, bg="white")
        white_area.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        #conversion ratio
        self.ratio_label = tk.Label(white_area, text=f"Ratio 1 : {round_to_sf(self.rate,3) if self.rate < 1 else round(self.rate,3)}", font=("Arial", 12), bg="#4682B4", fg="white", padx=5, pady=2) #self. because needs to be edited
        self.ratio_label.pack(pady=(20, 10))

        #conversion frame
        conversion_frame = tk.Frame(white_area, bg="white")
        conversion_frame.pack(pady=20)

        #input to convert
        input_frame = tk.Frame(conversion_frame, bg="#4682B4", padx=10, pady=10)
        input_frame.grid(row=0, column=0, padx=5)
        
        input_label = tk.Label(input_frame, text="Enter Amount", bg="#4682B4", fg="white", font=("Arial", 12))
        input_label.pack()
        
        self.input_entry = tk.Entry(input_frame, font=("Arial", 12), width=15) #self. because needs to be edited
        self.input_entry.pack(pady=(5, 0))
        self.input_entry.bind("<Return>", self.on_enter_pressed) #makes it so enter key makes the output show

        #code to have default text before click in
        self.placeholder_text = "Enter amount"
        self.input_entry.insert(0, self.placeholder_text)
        self.input_entry.config(fg='grey')
        self.input_entry.bind("<FocusIn>", self.on_entry_click)

        #equal sign
        equal_label = tk.Label(conversion_frame, text="=", font=("Arial", 16, "bold"), bg="white", fg="black")
        equal_label.grid(row=0, column=1, padx=10)

        #output after conversion
        output_frame = tk.Frame(conversion_frame, bg="#4682B4", padx=10, pady=10) #self. because needs to be edited
        output_frame.grid(row=0, column=2, padx=5)
        
        result_label = tk.Label(output_frame, text="Result", bg="#4682B4", fg="white", font=("Arial", 12))
        result_label.pack()
        
        self.output_entry = tk.Entry(output_frame, font=("Arial", 12), width=15)
        self.add_output_data(f"{0:.2f}")
        self.output_entry.pack(pady=(5, 0))

        #currency labels and swap button
        currency_frame = tk.Frame(white_area, bg="white")
        currency_frame.pack(pady=10)

        self.currency1_var = tk.StringVar(value=self.currency1)
        self.currency2_var = tk.StringVar(value=self.currency2)
        self.currency1_dropdown = ttk.Combobox(currency_frame, textvariable=self.currency1_var, 
                                       values=self.currencies, state="readonly", width=15, font=("Arial", 12))
        self.currency1_dropdown.grid(row=0, column=0, padx=5)

        swap_btn = tk.Button(currency_frame, text="Swap", bg="#4682B4", fg="white", font=("Arial", 12), width=10, command=self.swap)
        swap_btn.grid(row=0, column=1, padx=5)

        self.currency2_dropdown = ttk.Combobox(currency_frame, textvariable=self.currency2_var, 
                                       values=self.currencies, state="readonly", width=15, font=("Arial", 12))
        self.currency2_dropdown.grid(row=0, column=2, padx=5)
    
        self.currency1_var.trace_add('write', self.update_currency1)
        self.currency2_var.trace_add('write', self.update_currency2)

    def swap(self):
        """Swaps the 2 currencies, affects the rate and the output"""
        self.rate = 1/self.rate
        self.ratio_label.config(text=f"Ratio 1 : {round_to_sf(self.rate,3) if self.rate < 1 else round(self.rate,3)}")
        self.currency1 = self.currency2_var.get()
        self.currency2 = self.currency1_var.get()
        self.pair_label.config(text=f"{self.currency1} - {self.currency2}")
        self.currency1_var.set(self.currency1)
        self.currency2_var.set(self.currency2)
        self.add_output_data(self.convert_currency())        

    def on_enter_pressed(self, event):
        """Links to the input entry box"""
        value = self.input_entry.get()
        if not value:
            self.amount=0
            self.add_output_data(self.convert_currency())
            # self.output_setup()
        else:
            try:
                self.amount = float(value)
                self.add_output_data(self.convert_currency())
            except ValueError:
                self.amount = 0
                self.add_output_data("Error - Try Again")

    def on_entry_click(self, event):
        """Links to the input entry box"""
        if self.input_entry.get() == self.placeholder_text:
            self.input_entry.delete(0, "end")
            self.input_entry.config(fg='black')
    
    def add_output_data(self, result):
        """Adds data to output entry box"""
        self.output_entry.config(state='normal')
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, result)
        self.output_entry.config(state='readonly')
       
    def convert_currency(self):
        result = self.amount * self.rate 
        return f"{result:.2f}"

    def go_back(self):
        self.master.go_back()

    def update_currency1(self, *args):
        """Updates currency1 chosen to reflect selected one"""
        self.currency1 = self.currency1_var.get()
        self.rate = get_exchange_rate(self.currency1, self.currency2)
        self.ratio_label.config(text=f"Ratio 1 : {round_to_sf(self.rate,3) if self.rate < 1 else round(self.rate,3)}")
        self.pair_label.config(text=f"{self.currency1} - {self.currency2}")
        self.after(10, self.focus_input_entry)

    def update_currency2(self, *args):
        """Updates currency2 chosen to reflect selected one"""
        self.currency2 = self.currency2_var.get()
        self.rate = (get_exchange_rate(self.currency1, self.currency2))
        self.ratio_label.config(text=f"Ratio 1 : {round_to_sf(self.rate,3) if self.rate < 1 else round(self.rate,3)}")
        self.pair_label.config(text=f"{self.currency1} - {self.currency2}")
        self.after(10, self.focus_input_entry)

    def focus_input_entry(self):
        """Shifts focus to the input entry, and selects whole box"""
        self.input_entry.focus_set()
        #self.input_entry.select_range(0, tk.END) #may comment this out later, if found to be annoying in testing
        

class NotesPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#607D8B")
        self.master = master
        self.note_map = {}
        self.create_widgets()

    def create_widgets(self):
        title_frame = tk.Frame(self, bg="#947E9E")
        title_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        title_label = tk.Label(title_frame, text="Notes", font=("Arial", 24), bg="#947E9E", fg="white", padx=10, pady=5)
        title_label.pack(side=tk.LEFT)

        back_btn = tk.Button(self, text="Back", bg="#333940", fg="#FFEB3B",
                             font=("Arial", 10), padx=8, pady=4, width=8, command=self.go_back)
        back_btn.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="w")

        buttons_frame = tk.Frame(self, bg="#607D8B")
        buttons_frame.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

        other_buttons = [
            ("New Note", self.new_note),
            ("Save", self.save_note),
            ("Delete", self.delete_note),
        ]

        for index, (text, command) in enumerate(other_buttons):
            btn = tk.Button(buttons_frame, text=text, bg="#333940", fg="#FFEB3B", 
                            font=("Arial", 13), padx=11, pady=6, width=9, command=command)
            btn.grid(row=0, column=index, padx=2, pady=5)

        notes_frame = tk.Frame(self, bg="#333940", padx=10, pady=10)
        notes_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        notes_list_frame = tk.Frame(notes_frame, bg="#333940")
        notes_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        notes_label = tk.Label(notes_list_frame, text="Notes", font=("Arial", 14), bg="#333940", fg="#FFEB3B", pady=5)
        notes_label.pack(side=tk.TOP, anchor="w")

        self.notes_list = tk.Listbox(notes_list_frame, bg="white", fg="black", font=("Arial", 12), width=40)
        self.notes_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.notes_list.bind('<<ListboxSelect>>', self.on_select)
        self.notes_list.bind("<Double-1>", self.edit_title)

        notes_scrollbar = tk.Scrollbar(notes_list_frame, orient="vertical", command=self.notes_list.yview)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_list.config(yscrollcommand=notes_scrollbar.set)

        note_content_frame = tk.Frame(notes_frame, bg="#333940")
        note_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        edit_label = tk.Label(note_content_frame, text="Selected Note:", font=("Arial", 14), bg="#333940", fg="#FFEB3B", pady=5)
        edit_label.pack(side=tk.TOP, anchor="w")

        self.note_content = tk.Text(note_content_frame, wrap=tk.WORD, bg="white", fg="black", font=("Arial", 12))
        self.note_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content_scrollbar = tk.Scrollbar(note_content_frame, orient="vertical", command=self.note_content.yview)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.note_content.config(yscrollcommand=content_scrollbar.set)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.load_notes()

    def load_notes(self):
        self.notes_list.delete(0, tk.END)
        self.note_map = {}  # Dictionary to store note IDs
        
        notes = get_notes_list(logged_in_user)
        for note_id, title in notes:
            index = self.notes_list.size()
            self.notes_list.insert(tk.END, title)
            self.note_map[index] = note_id
        
        if self.notes_list.size() > 0:
            self.notes_list.selection_set(0)
            self.on_select(None)

    def on_select(self, event):
        if not self.notes_list.curselection():
            return

        index = self.notes_list.curselection()[0]
        self.current_note_id = self.note_map[index]
        
        # Clear current content
        self.note_content.delete('1.0', tk.END)
        
        # Get content by note ID
        content = get_note_content(self.current_note_id)
        if content:
            self.note_content.insert(tk.END, content)

    def save_note(self):
        if not self.notes_list.curselection():
            messagebox.showinfo("Info", "Please select a note to save.")
            return
        
        if not hasattr(self, 'current_note_id'):
            messagebox.showerror("Error", "No note selected.")
            return

        index = self.notes_list.curselection()[0]
        note_id = self.note_map[index]
        title = self.notes_list.get(index)
        content = self.note_content.get('1.0', tk.END).strip()
        
        if save_note_to_db(logged_in_user, title, content, note_id):
            messagebox.showinfo("Success", "Note saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save note.")

    def new_note(self):
        title = simpledialog.askstring("New Note", "Enter the title for the new note:")
        if title:
            content = ""
            note_id = save_note_to_db(logged_in_user, title, content)
            if note_id:
                self.load_notes()
                # Find and select the new note
                for i in range(self.notes_list.size()):
                    if self.notes_list.get(i) == title:
                        self.notes_list.selection_clear(0, tk.END)
                        self.notes_list.selection_set(i)
                        self.current_note_id = self.note_map[i]
                        self.notes_list.see(i)
                        break
                # Clear content area
                self.note_content.delete('1.0', tk.END)
            else:
                messagebox.showerror("Error", "Failed to create new note.")


    def edit_title(self, event):
        if not self.notes_list.curselection():
            return
        
        if hasattr(self, 'current_note_id') and self.current_note_id:
            old_title = self.notes_list.get(self.notes_list.curselection())
            new_title = simpledialog.askstring("Edit Title", "Enter new title:", initialvalue=old_title)
            
            if new_title and new_title != old_title:
                if update_note_title_in_db(self.current_note_id, new_title):
                    self.load_notes()
                else:
                    messagebox.showerror("Error", "Failed to update note title.")
        else:
            messagebox.showerror("Error", "No note selected.")

    def delete_note(self):
        if not self.notes_list.curselection():
            messagebox.showinfo("Info", "Please select a note to delete.")
            return
        
        if hasattr(self, 'current_note_id') and self.current_note_id:
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?"):
                if delete_note_from_db(self.current_note_id):
                    self.load_notes()
                else:
                    messagebox.showerror("Error", "Failed to delete note.")
        else:
            messagebox.showerror("Error", "No note selected.")

    def go_back(self):
        self.master.go_back()


if __name__ == "__main__":
    app = CryptoTrackerApp()
    app.mainloop()
    
