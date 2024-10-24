import tkinter as tk
from tkinter import font as tkfont
from tkinter import simpledialog, messagebox, ttk
from apifunctions import get_price_tracker_data, get_exchange_rate, get_formatted_news, get_coin_ticker_with_key, get_coin_id_from_ticker
from mathfunctions import round_to_sf, merge, merge_sort
from sqlcode import add_new_user, check_username_exists, add_coin_to_list, remove_coin_from_list, add_transaction_to_db, add_coin_to_database, fetch_transactions
from sqlcode import save_note_to_db, delete_note_from_db, get_note_from_db, get_all_note_titles, update_note_title_in_db
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

        #headers for the coin list (TODO make them sortable)
        #TODO make percentages rounded, and make market cap have commas
        #TODO make width of header smaller, and that it cant be moved, then reduce geometry size back to 1280x720
        columns=("Name", "Ticker", "Price (USD)", "1h Change (%)", "24h Change (%)", "7d Change (%)", "Market Cap (USD)", "Rank (Market Cap)")
        self.coin_list = ttk.Treeview(top_coins_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.coin_list.heading(col, text=col)
        self.coin_list.pack(fill=tk.BOTH, expand=True)

        coins = get_top_coins(logged_in_user)
        coins.reverse()
        if len(coins) > 100:
            coins = coins[:100]
        data = get_price_tracker_data(coins)
        for coin in coins:
            self.coin_list.insert("",0,values=data[coin])

        #configures grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def add_coin(self):
        coin = simpledialog.askstring("Add Coin", "Enter the name of the coin:").lower()
        if coin == "xrp":
            messagebox.showerror("Error", f"Failed to add {coin}. It may already be in your list or not exist in our database.")
        elif coin:
            coin = coin.strip()
            success = add_coin_to_list(logged_in_user, coin)
                
            if success:
                messagebox.showinfo("Success", f"{coin} has been added to your list.")
                self.refresh_data()
            else:
                messagebox.showerror("Error", f"Failed to add {coin}. It may already be in your list or not exist in our database.")
    
    def remove_coin(self):
        selected_items = self.coin_list.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a coin to remove.")
            return None
        
        total_coins = len(self.coin_list.get_children())
        if total_coins == 1:
            messagebox.showerror("Error", "Cannot remove the last coin. Your list must contain at least one coin.")
            return None
    
        item = selected_items[0]
        coin_data = self.coin_list.item(item, "values")
        coin_ticker = coin_data[1]
        if coin_ticker =="xrp":
            coin_ticker = "rlusd"
        confirm = messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove {coin_ticker}?")
        if confirm:
            success = remove_coin_from_list(logged_in_user, coin_ticker)
            if coin_ticker =="rlusd":
                coin_ticker = "xrp"
            if success:
                self.refresh_data()
                messagebox.showinfo("Success", f"{coin_ticker} has been removed from your list.")
            else:
                messagebox.showerror("Error", f"Failed to remove {coin_ticker} from your list.")

    def sort(self):
        # Create a custom dialog for sorting options
        sort_dialog = tk.Toplevel(self)
        sort_dialog.title("Sort Options")
        sort_dialog.geometry("300x150")
        sort_dialog.resizable(False, False)

        # Create and pack widgets
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
            
            # Get all items in the treeview
            data = [(self.coin_list.set(child, column), child) for child in self.coin_list.get_children('')]

            # Define key function for sorting
            def key_function(item):
                return self.convert_value(item[0], column)

            # Sort the data using merge sort
            sorted_data = merge_sort(data, key_function)

            # Reverse if descending order
            if reverse:
                sorted_data.reverse()

            # Rearrange items in sorted positions
            for index, (_, child) in enumerate(sorted_data):
                self.coin_list.move(child, '', index)

            sort_dialog.destroy()

        tk.Button(sort_dialog, text="Apply", command=apply_sort).pack(pady=10)

        # Wait for the dialog to be closed
        self.wait_window(sort_dialog)

    def convert_value(self, value, column):
        if column in ["Price (USD)", "1h Change (%)", "24h Change (%)", "7d Change (%)"]:
            return float(value.strip('%$').replace(',', ''))
        elif column == "Market Cap (USD)":
            return int(value.strip('$').replace(',', ''))
        elif column == "Rank (Market Cap)":
            return int(value)
        else:
            return value.lower()


        
    def go_back(self):
        self.master.go_back()

    def refresh_data(self):
        self.master.refresh_page()
    

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
            ("Filters", None),
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
        
        #filters  None values and collects valid coin IDs
        valid_coin_ids = []
        for coin in transactions.keys():
            coin_id = get_coin_id_from_ticker(coin)
            if coin_id is not None:
                valid_coin_ids.append(coin_id)
            else:
                print(f"Warning: Could not get coin ID for ticker {coin}")

        if not valid_coin_ids:
            messagebox.showwarning("No Data", "No valid coin data available to display.")
            return

        current_prices = get_price_tracker_data(valid_coin_ids)
        
        for coin, data in transactions.items():
            quantity = data['quantity']
            price_bought = data['total_value']
            
            coin_id = get_coin_id_from_ticker(coin)
            if coin_id is None:
                continue 

            coin_data = current_prices.get(coin_id, [])
            current_price = coin_data[2] if len(coin_data) >= 3 else 0
            
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
        if value is None:
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
    
        #TODO add to coin table if not exist in db already

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


    def get_chart(self):
        ...

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
        self.create_widgets()

    def create_widgets(self):
        
        title_frame = tk.Frame(self, bg="#947E9E")
        title_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        title_label = tk.Label(title_frame, text="Notes", font=("Arial", 24), bg="#947E9E", fg="white", padx=10, pady=5)
        title_label.pack(side=tk.LEFT)

        back_btn = tk.Button(self, text="Back", bg="#333940", fg="#FFEB3B",
                             font=("Arial", 10), padx=8, pady=4, width=8, command=self.go_back)
        back_btn.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="w")

        #creating other buttons
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

        #notes section
        notes_frame = tk.Frame(self, bg="#333940", padx=10, pady=10)
        notes_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        #notes list on left
        notes_list_frame = tk.Frame(notes_frame, bg="#333940")
        notes_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        notes_label = tk.Label(notes_list_frame, text="Notes", font=("Arial", 14), bg="#333940", fg="#FFEB3B", pady=5)
        notes_label.pack(side=tk.TOP, anchor="w")

        self.notes_list = tk.Listbox(notes_list_frame, bg="white", fg="black", font=("Arial", 12), width=40)
        self.notes_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.notes_list.bind('<<ListboxSelect>>', self.on_select)
        self.notes_list.bind("<Double-1>", self.edit_title)

        #scrollbar for notes list
        notes_scrollbar = tk.Scrollbar(notes_list_frame, orient="vertical", command=self.notes_list.yview)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_list.config(yscrollcommand=notes_scrollbar.set)

        #text box for notes
        note_content_frame = tk.Frame(notes_frame, bg="#333940")
        note_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        edit_label = tk.Label(note_content_frame, text="Selected Note:", font=("Arial", 14), bg="#333940", fg="#FFEB3B", pady=5)
        edit_label.pack(side=tk.TOP, anchor="w")

        self.note_content = tk.Text(note_content_frame, wrap=tk.WORD, bg="white", fg="black", font=("Arial", 12))
        self.note_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        #scrollbar for notes
        content_scrollbar = tk.Scrollbar(note_content_frame, orient="vertical", command=self.note_content.yview)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.note_content.config(yscrollcommand=content_scrollbar.set)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.load_notes()

    def go_back(self):
        self.master.go_back()

    def new_note(self):
        title = simpledialog.askstring("New Note", "Enter the title for the new note:")
        if title:
            content = ""
            note_id = save_note_to_db(logged_in_user, title, content)
            if note_id:
                self.load_notes()
                self.current_note_id = note_id
                self.note_content.delete('1.0', tk.END)
                self.select_note_by_title(title)
            else:
                messagebox.showerror("Error", "Failed to create new note.")

    def save_note(self):
        if not self.notes_list.curselection():
            messagebox.showinfo("Info", "Please select a note to save or create a new one.")
            return
        
        title = self.notes_list.get(tk.ACTIVE)
        content = self.note_content.get('1.0', tk.END).strip()
        if self.current_note_id:
            success = save_note_to_db(logged_in_user, title, content, self.current_note_id)
        else:
            self.current_note_id = save_note_to_db(logged_in_user, title, content)
            success = bool(self.current_note_id)
        
        if success:
            messagebox.showinfo("Success", "Note saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save note.")

    def delete_note(self):
        if not self.notes_list.curselection():
            messagebox.showinfo("Info", "Please select a note to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?"):
            if delete_note_from_db(self.current_note_id):
                self.load_notes()
                self.note_content.delete('1.0', tk.END)
                self.current_note_id = None
            else:
                messagebox.showerror("Error", "Failed to delete note.")

    def on_select(self, event):
        if not self.notes_list.curselection():
            return
        index = self.notes_list.curselection()[0]
        title = self.notes_list.get(index)
        note = get_note_from_db(logged_in_user, title)
        if note:
            self.current_note_id, content = note
            self.note_content.delete('1.0', tk.END)
            self.note_content.insert(tk.END, content)
        else:
            messagebox.showerror("Error", "Failed to load note content.")

    def edit_title(self, event):
        if not self.notes_list.curselection():
            return
        old_title = self.notes_list.get(self.notes_list.curselection())
        new_title = simpledialog.askstring("Edit Title", "Enter new title:", initialvalue=old_title)
        if new_title and new_title != old_title:
            if update_note_title_in_db(self.current_note_id, new_title):
                self.load_notes()
                self.select_note_by_title(new_title)
            else:
                messagebox.showerror("Error", "Failed to update note title.")

    def load_notes(self):
        self.notes_list.delete(0, tk.END)
        titles = get_all_note_titles(logged_in_user)
        for title in titles:
            self.notes_list.insert(tk.END, title)
        if titles:
            self.notes_list.selection_set(0)
            self.on_select(None)

    def select_note_by_title(self, title):
        for i in range(self.notes_list.size()):
            if self.notes_list.get(i) == title:
                self.notes_list.selection_clear(0, tk.END)
                self.notes_list.selection_set(i)
                self.notes_list.see(i)
                self.on_select(None)
                break

if __name__ == "__main__":
    app = CryptoTrackerApp()
    app.mainloop()
    
