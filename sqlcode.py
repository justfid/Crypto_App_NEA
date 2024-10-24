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


def remove_coin_from_list(username, coinTicker):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    coinTicker = coinTicker.upper()
    if coinTicker:
        #removes coin from user's list
        query = "DELETE FROM TopcoinList WHERE listOwner = ? AND coinTicker = ?;"
        try:
            cursor.execute(query, (username, coinTicker,))
            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                return False  #coin was not in user's list
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            connection.close()
    else:
        connection.close()
        return False  #invalid coin name


def add_transaction_to_db(username, coin_ticker, value, quantity):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    query = "INSERT INTO Transactions (portfolioOwner, coinTicker, value, quantity) VALUES (?, ?, ?, ?);"
    try:
        cursor.execute(query, (username, coin_ticker, value, quantity))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        connection.close()

def check_ticker_exists(ticker):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
        
    query = "SELECT coinTicker FROM Coin WHERE coinTicker = ?;"
    cursor.execute(query, (ticker,))
    result = cursor.fetchone()
        
    connection.close()
    return result is not None

if __name__ == "__main__":
    pass

def fetch_transactions(username):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    query = """
    SELECT coinTicker,
           SUM(value) as total_value,
           SUM(quantity) as total_quantity
    FROM Transactions
    WHERE portfolioOwner = ?
    GROUP BY coinTicker
    """
    
    try:
        cursor.execute(query, (username,))
        results = cursor.fetchall()
        
        transactions = {}
        for row in results:
            coin, total_value, total_quantity = row
            transactions[coin] = {
                'total_value': total_value,
                'quantity': total_quantity
            }
        
        return transactions
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {}
    finally:
        connection.close()


def save_note_to_db(username, title, content, note_id=None):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    try:
        if note_id:
            cursor.execute("UPDATE NotesData SET title=?, content=? WHERE noteId=?", (title, content, note_id))
            connection.commit()
            return note_id
        else:
            cursor.execute("INSERT INTO NotesData (title, content, noteOwner) VALUES (?, ?, ?)", (title, content, username))
            connection.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        connection.close()

def delete_note_from_db(note_id):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM NotesData WHERE noteId=?", (note_id,))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        connection.close()

def get_note_from_db(username, title):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT noteId, content FROM NotesData WHERE title=? AND noteOwner=?", (title, username))
        result = cursor.fetchone()
        return result if result else (None, "")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None, ""
    finally:
        connection.close()

def get_all_note_titles(username):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT title FROM NotesData WHERE noteOwner=?", (username,))
        titles = [row[0] for row in cursor.fetchall()]
        return titles
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        connection.close()

def update_note_title_in_db(note_id, new_title):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE NotesData SET title=? WHERE noteId=?", (new_title, note_id))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        connection.close()