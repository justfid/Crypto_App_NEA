import hashlib
import sqlite3

db_path = "CryptoApp.db"


def verify_password(provided_password, username):
    """verifies to see if stored (hashed) password is the same as the hashed new password for the user given"""
    stored_password = get_hashed_password(username)
    salt = bytes.fromhex(stored_password[:64]) #extracts salt from stored password (first 64 chars / 32 bytes)
    stored_hash = bytes.fromhex(stored_password[64:]) #extracts stored hash (after 64 chars)
    
    iterations = 100_000 #same parameters used in hash_password
    key_length = 32
    
    #hashes provided password with the extracted salt
    new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, iterations, key_length)
    #compares new hash with stored hash: == in python is a timing-safe comparison
    return new_hash == stored_hash

def get_hashed_password(username):
    """returns the hashes password of a user"""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    query = "SELECT hashedPassword FROM User WHERE username = ?;"
    try:
        cursor.execute(query, (username,))
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

    
def get_top_coins(username):
    """returns the list of top coins"""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    query = "SELECT coinName FROM Coin INNER JOIN TopcoinList ON Coin.coinTicker = TopcoinList.coinTicker WHERE listOwner= ?;"
    try:
        cursor.execute(query, (username,))
        result = cursor.fetchall()
        formatted_result = [item[0] for item in result]
        if result:
            return formatted_result
        else:
            return None  # TODO need error handling
    except sqlite3.Error as e:
        print(f"Database error: {e}") #TODO see if this is needed
        return None
    finally:
        connection.close()

