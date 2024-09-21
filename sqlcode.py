import sqlite3
from mathfunctions import hash_password
from apifunctions import get_coin_ticker_with_key

db_path = "CryptoApp.db"

def add_new_user(username, password):
    """adds new user to database"""
    hashed_password = hash_password(password)
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    query = "INSERT INTO User (username, hashedPassword) VALUES (?, ?)"
    try:
        cursor.execute(query, (username, hashed_password))
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as e:
        return False
    finally:
        connection.close()


def check_username_exists(username):
    "returns boolean"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    query = "SELECT username FROM User WHERE username = ?;"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    connection.close()
    if result:
        return True
    else:
        return False
    

def add_coin_to_list(username, coinName):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    #checks to see if its a valid coin
    coinTicker = get_coin_ticker_with_key(coinName)
    if coinTicker:
        
        db_query = "SELECT coinName from Coin WHERE coinName = ?;"
        cursor.execute(db_query, (coinName,))
        result = cursor.fetchone()
        #checks if coin in coin table, if not it adds it
        if not result:
            add_coin_to_database(coinTicker, coinName)
    
        query = "INSERT INTO TopcoinList (listOwner, coinTicker) VALUES (?,?);"
        try:
            cursor.execute(query, (username, coinTicker,))
        except sqlite3.IntegrityError:
            return False
        else:
            return True
        finally:
            connection.commit()
            connection.close()
    else:
        connection.close()
        return False


def add_coin_to_database(coinTicker, coinName):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    query = "INSERT INTO Coin (coinTicker, coinName) VALUES (?,?);"
    cursor.execute(query, (coinTicker, coinName,))
    connection.commit()
    connection.close()

if __name__ == "__main__":
    add_coin_to_list("t","chainlink")