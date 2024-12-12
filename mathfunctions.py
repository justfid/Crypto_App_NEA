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
    iterations = 100_000 #number of iterations for PBKDF2 algorithm (more means more security but longer time)
    key_length = 32 #length of hashed password in bytes
    
    #hashes password with PBKDF2 using sha256 within
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, key_length) 
        #password.encode() converts string to bytes
    return salt.hex() + password_hash.hex() #combines salt and hash, converting both to hexadecimal strings


def merge_sort(arr, key_function=None):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key_function) #recursion
    right = merge_sort(arr[mid:], key_function) #recursion

    return merge(left, right, key_function)

def merge(left, right, key_function):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        left_value = key_function(left[i]) if key_function else left[i]
        right_value = key_function(right[j]) if key_function else right[j]
        
        if left_value <= right_value:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


if __name__ == "__main__":
    ...
