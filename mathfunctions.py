import math
import os
import hashlib

def round_to_sf(x, sf=3):
    if x == 0:
        return 0
    return round(x, -int(math.floor(math.log10(abs(x)))) + (sf - 1))


def hash_password(password):
    """hashes passsword with salt into 32 bytes - as a hex string"""
    salt = os.urandom(32) #generates random salt for password (32 bytes)
    iterations = 100_000 #number of iterations for PBKDF2 algorithm (more means more security but longer time TODO pick a suitable value)
    key_length = 32 #length of hashed password in bytes
    
    #hashes password with PBKDF2 using sha256 within
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, key_length) #password.encode() converts string to bytes
    return salt.hex() + password_hash.hex() #combines salt and hash, converting both to hexadecimal strings

if __name__ == "__main__":
    ...
