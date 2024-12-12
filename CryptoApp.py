#import libraries needed
from frames import CryptoTrackerApp
import sqlite3


def initialise_database():
    """creates tables if they don't already exist"""
    conn = sqlite3.connect('CryptoApp.db')
    cursor = conn.cursor()

    #SQL initialization statements
    initialization_sql = """
    CREATE TABLE IF NOT EXISTS User (
        username VARCHAR NOT NULL UNIQUE,
        hashedPassword TEXT NOT NULL,
        PRIMARY KEY(username)
    );

    CREATE TABLE IF NOT EXISTS NotesData (
        noteId INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR NOT NULL,
        content TEXT, 
        noteOwner VARCHAR NOT NULL,
        FOREIGN KEY(noteOwner) REFERENCES User(username)
    );

    CREATE TABLE IF NOT EXISTS TopcoinList (
        listOwner VARCHAR NOT NULL,
        coinTicker VARCHAR NOT NULL,
        PRIMARY KEY(listOwner, coinTicker),
        FOREIGN KEY(listOwner) REFERENCES User(username),
        FOREIGN KEY(coinTicker) REFERENCES Coin(coinTicker)
    );

    CREATE TABLE IF NOT EXISTS Transactions (
        transactionId INTEGER PRIMARY KEY AUTOINCREMENT,
        value FLOAT,
        quantity FLOAT, 
        portfolioOwner VARCHAR NOT NULL,
        coinTicker VARCHAR NOT NULL,
        FOREIGN KEY(portfolioOwner) REFERENCES User(username),
        FOREIGN KEY(coinTicker) REFERENCES Coin(coinTicker)
    );

    CREATE TABLE IF NOT EXISTS Coin (
        coinTicker VARCHAR NOT NULL UNIQUE,
        coinName VARCHAR NOT NULL,
        PRIMARY KEY(coinTicker)
    );
    """
    
    #execute each statement
    for statement in initialization_sql.split(';'):
        if statement.strip():
            cursor.execute(statement)
    
    conn.commit()
    conn.close()


#runs application
if __name__ == "__main__":
    initialise_database()
    app = CryptoTrackerApp()
    app.mainloop()


