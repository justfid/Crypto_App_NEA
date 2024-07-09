import requests
import sqlite3
import matplotlib
from windows import CryptoTrackerApp, LoginPage

if __name__ == "__main__":
    app = CryptoTrackerApp()
    app.bind("<Configure>", app.on_resize)
    app.mainloop()