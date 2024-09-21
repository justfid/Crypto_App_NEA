import sqlite3
from mathfunctions import hash_password

db_path = "CryptoApp.db"

def add_new_user(username, password):
    """adds new user to database"""
    hashed_password = hash_password(password)
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    try:
        cursor.execute("INSERT INTO User (username, hashedPassword) VALUES (?, ?)",
                       (username, hashed_password))
        connection.commit()
        print(f"User '{username}' added successfully.")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Username '{username}' already exists.")
        return False
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        connection.close()


def check_username_exists(username):
    "returns boolean"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT username FROM User WHERE username = ?;", (username,))
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False
    except sqlite3.Error as e:
        print(f"Database error: {e}") #TODO see if this is needed
        return False
    finally:
        connection.close()


def get_hashed_password(username):
    """returns the hashes password of a user"""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT hashedPassword FROM User WHERE username = ?;", (username,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return the hashed password
        else:
            return None  # User not found TODO will raise error in mathfunction if none - see if theres any case this is none
    except sqlite3.Error as e:
        print(f"Database error: {e}") #TODO see if this is needed
        return None
    finally:
        connection.close()


# Example usage
if __name__ == "__main__":
    print(get_hashed_password("test"))