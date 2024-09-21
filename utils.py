import hashlib
from sqlcode import get_hashed_password

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

if __name__ == "__main__":
    verify_password("test","test")