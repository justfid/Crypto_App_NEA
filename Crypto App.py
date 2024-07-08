import tkinter as tk
import requests
import sqlite3
import matplotlib

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Cryptocurrency Price Tracker & Portfolio Manager")
        self.geometry("1920x1080")
        self.resizable(True, True)

        self.frames = {}

        for eachFrame in (homeFrame, loginFrame, priceFrame, portfolioFrame):
            specificFrame = eachFrame(self)
            self.frames[eachFrame] = specificFrame
            specificFrame.grid(row = 0, column = 0, sticky="nsew")

        #change it so frame is made when needed, rather than all at the start

        self.showFrame(loginFrame)

    def showFrame(self, frameName):
        frame = self.frames[frameName]
        frame.tkraise()


class loginFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.header = tk.Label(self, text="Login", font=("Helvetica", 16))
        self.header.grid(row = 0, column = 0, columnspan=2, sticky="nsew")

        self.usernameLabel = tk.Label(self, text="Username:")
        self.usernameLabel.grid(row = 1, column = 0)
        self.usernameBox = tk.Entry(self)
        self.usernameBox.grid(row = 1, column = 1)
        
        self.passwordLabel = tk.Label(self, text="Password:")
        self.passwordLabel.grid(row = 2, column = 0)
        self.passwordBox = tk.Entry(self, show = "*")
        self.passwordBox.grid(row = 2, column = 1)

        self.loginButton = tk.Button(self, text = "Login", command = self.login)
        self.loginButton.grid(row = 3, columnspan = 2)

    def login(self):
        username = self.usernameBox.get()
        password = self.passwordBox.get()
        #add logic here - if statement to see if its right
        app.showFrame(homeFrame)

class homeFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.header = tk.Label(self, text="Home", font=("Helvetica", 16))
        self.header.grid(row = 0, column = 0, columnspan=2, sticky="nsew")

        self.priceLabel = tk.Label(self, text="Price Tracker")
        self.priceLabel.grid(row = 1, column = 0)

        self.portfolioLabel = tk.Label(self, text="Portfolio Manager")
        self.portfolioLabel.grid(row = 1, column = 1)

        self.priceButton = tk.Button(self, text = "Select", command = self.showPrice)
        self.priceButton.grid(row = 2, column = 0)

        self.portfolioButton = tk.Button(self, text = "Select", command = self.showPortfolio)
        self.portfolioButton.grid(row = 2, column = 1)

        self.logoutButton = tk.Button(self, text = "Logout", command = self.logout)
        self.logoutButton.grid(row = 3, column = 0)

    def logout(self):
        app.showFrame(loginFrame)

    def showPrice(self):
        app.showFrame(priceFrame)

    def showPortfolio(self):
        app.showFrame(portfolioFrame)


class priceFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.header = tk.Label(self, text="Price Tracker", font=("Helvetica", 14))
        self.header.grid(row = 0, column = 0, columnspan=2, sticky="nsew")

        self.btcLabel = tk.Label(self, text="Bitcoin Price:")
        self.btcLabel.grid(row = 1, column = 0)
        self.btcPrice = get_bitcoin_price()
        #this gets called once when the frame is created - it wont update after that for the lifecycle of the program
        self.btc = tk.Label(self, text=self.btcPrice)
        self.btc.grid(row = 1, column = 1)

        self.backButton = tk.Button(self, text = "Back", command = self.home)
        self.backButton.grid(row = 2)

    def home(self):
        app.showFrame(homeFrame)

class portfolioFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.header = tk.Label(self, text="Portfolio Manager", font=("Helvetica", 14))
        self.header.grid(row = 0, column = 0, columnspan=2, sticky="nsew")

        self.backButton = tk.Button(self, text = "Back", command = self.home)
        self.backButton.grid(row = 3)

    def home(self):
        app.showFrame(homeFrame)

def get_bitcoin_price():
    url =  "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin&x_cg_demo_api_key=CG-ENPhPS4nXXeKYt64emtmqGRv"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data):
            bitcoin_price = data[0]['current_price']
            return bitcoin_price
        else:
            print("Bitcoin data not found")
            return "Data Not Available"
    else:
        print("Error fetching data:", response.status_code)
        return "Error"


if __name__ == "__main__":
    app = App()
    app.mainloop()

