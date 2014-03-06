import base64

# base64.b64encode(b'hello')
# base64.b32encode(b'hello')
# base64.b16encode(b'hello')

# 'hello'.encode() -> b'hello'

import hashlib

# hashlib.sha256(b'hello').hexdigest()
# hashlib.md5(b'hello').hexdigest()

import binascii

# binascii.b2a_hex(b'hello') -> b'68656c6c6f'

import os

# os.urandom(4)

from math import ceil

# Convert an integer to a byte string
def int2bstr(num):
    length = max((num.bit_length()-1) // 8 + 1, 1)
    return num.to_bytes(length, byteorder='big')

# Convert a byte string to an integer
def bstr2int(bstr):
    return int.from_bytes(bstr, byteorder='big')

# Return the MD5 hash of the data, truncated to at most "bytes" bytes.
# By default, the number of bytes is 16 (the full size of MD5).
def md5(data, bytes=16):
    md5 = hashlib.md5(data).digest()
    return md5[-bytes:]

# Return base64 encoding of an int, string, or byte string.
# Return value is a base-64 encoded byte string
def to_base64(s):
    if type(s) is bytes:
        return base64.b64encode(s)
    elif type(s) is str:
        return base64.b64encode(s.encode())
    elif type(s) is int:
        return base64.b64encode(int2bstr(s))
    else:
        return b''

# Return a byte string from a base-64 encoded byte string
def from_base64(s, fmt=bytes):
    if fmt is bytes:
        return base64.b64decode(s)
    elif fmt is int:
        return bstr2int(base64.b64decode(s))
    elif fmt is str:
        return base64.b64decode(s).decode()
    else:
        return b''

def to_base58check(s):
    code_string = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    if type(s) is bytes:
        x = bstr2int(s)
    elif type(s) is str:
        x = bstr2int(s.encode())
    elif type(s) is int:
        x = s
    else:
        return b''

    output_string = b''
    while (x > 0):
        (x, r) = divmod(x, 58)
        output_string = output_string + code_string[r].encode()

    return output_string[::-1]

# "Solve" a block of data.
# Generates a random nonce (32 bits) and appends it to the data.
# Run this string through the MD5 hash algorithm.
# The block is solved if the hash hash a prefix of at least "difficulty" bits.
# Optional: reduce the size of the hash string by passing the "bytes"
#   argument.
# Optional: limit the number of iterations by passing the "limit" argument.
def solve(block, difficulty, limit=2**32, bytes=16):
    bits = bytes * 8
    target =  2 ** (bits - difficulty)
    while (limit > 0):
        nonce = os.urandom(4)
        bstr = block + nonce
        md5str = md5(bstr, bytes)
        md5int = bstr2int(md5str)
        if md5int < target:
            return (bstr2int(nonce), binascii.b2a_hex(md5str))
        else:
            limit = limit - 1
    else:
        return (0,0)

# Each item can be up to 65535 bytes in length.
# Will truncate data silently.
def serialize(arr):
    """Serialize an array of byte strings"""
    
    out_str = b''
    
    for item in arr:
        if type(item) is str:
            item = item.encode()
        length = min(len(item), 65535)
        item = item[0:length]
        header = int2bstr(length).rjust(2, b'\x00')
        out_str = out_str + header + item

    return out_str

def deserialize(bstr):
    """Return an array of byte strings from a serialized string"""
    if len(bstr) < 2:
        return []

    arr = []
    
    i = 0
    while i < len(bstr):
        length = bstr2int(bstr[i:i+2])
        data = bstr[i+2:i+2+length]
        arr += [data]
        i = i + 2 + length

    return arr

# Decode a key, assumed to be an int.
# Returns (e, n)
def key_decode(key):
    bstr = int2bstr(key)
    e_str_len = bstr[0]          # First byte contains the length of e
    e_str = bstr[1:e_str_len+1]  # Get e out of the string
    n_str = bstr[e_str_len+1:]   # Get n out of the string
    e = bstr2int(e_str)          # Convert to int
    n = bstr2int(n_str)          # Convert to int
    return (e, n)

# Encode a key into an int.
# The format of the number is:
#   First byte: length of e (in bytes)
#   Followed by e
#   Followed by n
def key_encode(e, n):
    e_str = int2bstr(e)
    n_str = int2bstr(n)
    e_str_len = int2bstr(len(e_str))
    return bstr2int(e_str_len + e_str + n_str)


# The modulus of the key is assumed to be larger than the data to be
# encrypted.
def encrypt(data, key):
    """Encrypt a blob of data using a key."""
    if type(key) is tuple:
        (e, n) = key
        return pow(data, e, n)
    elif type(key) is int:
        (e, n) = key_decode(key)
        return pow(data, e, n)

def encrypt_str(str, key):
    """Encrypt a string using a key"""
    # Extract key parts
    if type(key) is int:
        (e, n) = key_decode(key)
    elif type(key) is tuple:
        (e, n) = key

    # Encode str into a byte string, if necessary
    if type(str) is str:
        str = str.encode()
        
    # Calculate input chunk size, rounded down to nearest 8 bits
    in_chunk_size = n.bit_length() // 8

    # Calculate output chunk size, rounded up to nearest 8 bits
    out_chunk_size = n.bit_length() // 8 + 1

    # Put together the header
    last_chunk_size = len(str) % in_chunk_size
    header = b'\x04' + int2bstr(in_chunk_size) + \
             int2bstr(out_chunk_size) + int2bstr(last_chunk_size)

    # Start the output string
    out_str = b''

    # Encrypt each chunk, appending to out_str
    for i in range(0, len(str), in_chunk_size):
        in_chunk = str[i:i+in_chunk_size]
        out_chunk = int2bstr(encrypt(bstr2int(in_chunk), key))
        out_str = out_str + out_chunk.rjust(out_chunk_size, b'\x00')
    
    return header + out_str

def decrypt_str(bstr, key):
    """Decrypt an encrypted byte string using a key"""
    # Extract header parts
    data_start = bstr[0]
    out_chunk_size = bstr[1]
    in_chunk_size = bstr[2]
    last_chunk_size = bstr[3]

    # Start the output string
    out_str = b''

    # Decrypt each chunk, appending to out_str
    for i in range(data_start, len(bstr), in_chunk_size):
        in_chunk = bstr[i:i+in_chunk_size]
        out_chunk = int2bstr(encrypt(bstr2int(in_chunk), key))
        if i + in_chunk_size < len(bstr):
            out_str = out_str + out_chunk.rjust(out_chunk_size, b'\x00')
        else:
            out_str = out_str + out_chunk

    return out_str

# Return encrypted hash of data.
# Data is assumed to be a byte string (ie, already encoded).
# Key is an encoded key (int).
def sign(data, key):
    """Return an encrypted hash of data using a key"""
    md5str = md5(data, 16)
    signature = encrypt_str(md5str, key)
    return signature

def my_address(pub_key):
    """Calculate the address from the public key"""
    if type(pub_key) is int:
        h = md5(int2bstr(pub_key))
    elif type(pub_key) is tuple:
        (e, n) = pub_key
        k = key_encode(e, n)
        h = md5(int2bstr(k))
    return to_base58check(h).decode()

def gcd(a, b):
    if b == 0:
        return a
    else:
        return gcd(b, a % b)

def egcd(a, b):
    if b == 0:
        return (1, 0)
    else:
        (q, r) = divmod(a, b)
        (s, t) = egcd(b, r)
        return (t, s-q*t)
    
def phi(p, q):
    return (p-1)*(q-1)

def finde(p, q):
    return [e for e in range(2, phi(p, q)) if gcd(e, phi(p, q)) == 1]

def findd(e, t):
    (x, y) = egcd(e, t)
    return x % t

def genkeys(p, q):
    """Return the public and private keys, encoded as ints"""
    e = 65537
    n = p * q
    d = findd(e, phi(p, q))
    return (key_encode(e, n), key_encode(d, n))


