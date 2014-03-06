# About

People have been asking me about Bitcoin: what it is and how it works. I can explain
what it is pretty easily, but how it works is more complex. While a student can read
about its inner workings, seeing it in action is difficult since running a real
Bitcoin/Litecoin/Dogecoin client costs real money to buy in. The source code is also
difficult for the beginner to comprehend.

Mycoin (for lack of a better name) is an attempt to create a set of Python functions
to simulate the Bitcoin protocol.

# (Planned) Features

* Purely functional. No objects or methods.
* Inputs and ouputs are human-readable: tuples, lists, ints, dictionaries, and byte strings.
* Uses MD5 rather than SHA256 because the hash size is smaller and therefore easier to visually inspect. Libraries include wrappers for MD5 that allow the hash size to be reduced further.

# Limitations

* No peer-to-peer networking. Use some other broadcast mechanism, such as an email list.
* No blocks. Miners solve individual transactions. The blockchain is therefore just a list of transactions.
* Client is just the IDLE shell. No support for wallet-like functionality, such as maintaining a list of private keys. Therefore...
* Only explicit support for one public/private key per user. Should be sufficient for a simulation.
* User addresses are encoded in base-58 (like Bitcoin addresses), but don't include a checksum. This keeps them relatively short.

# Sample Usage

To keep the numbers relatively small, we will use 32-bit (4-byte) hashes. Since MD5 is normally 128 bits
(16 bytes), our wrapper md5 function allows us to keep only the lower n bytes. Also, since we are
using 32 bits, we need to make sure our RSA modulus is at least 32 bits. This means using 17-bit primes to
generate the keys.

Start by picking two 17-bit primes. I used the Miller-Rabin Primality tester to determine whether my candidates
are actually prime. I choose p=97859 and q=112139.

    >>> (pub, priv) = genkeys(97859, 112139)
    >>> pub
    1223111366094295328558817
    >>> priv
    315475364093914817328778977
    
The keys contain the exponent and modulus serialized into an int.
Each serialized item is prefixed with the length of the item (in bytes). The first byte of the serialization
is how long each length header is.

    >>> hex(pub)
    '0x10301000105028e170ee1'


Broken down:

* 0x1 -> Each serialized item is prefixed with 1 byte that is the length of the item.
* 0x03 -> The first item is 3 bytes long.
* 0x010010 -> The exponent is 65537.
* 0x05 -> The length of the next item is 5 bytes.
* 0x028e170ee1 -> The modulus is 10973810401. It is more than 32 bits long, so we're good to encrypt data that is up to 32 bits.

We can use key_decode to extract the components of the key:

    >>> key_decode(pub)
    (65537, 10973810401)
    >>> key_decode(priv)
    (4102144381, 10973810401)
    
Now we can use our keys to encrypt and decrypt data. First we'll encrypt a blob of data. Since our modulus is a 33- or 34-bit number, we can encrypt data that is at most about 32 bits long. Let's encrypt the string b'Hi!'. (Reminder: in Python, b'foo' notation represents a byte string; that is, a three-byte string (or array) consisting of the ASCII values for 'f', 'o', and 'o'.) Most of the functions in this library work on either byte strings or ints. Our encryption function works on ints, so we need to convert the bytestring to an int using bstr2int.

Encrypt the string using the private key.

    >>> i = bstr2int(b'Hi!')
    >>> i
    4745505
    >>> encrypt(i, priv)
    2750689767
    
Alternatively, just put it all together by nesting functions:

    >>> ciphertext = encrypt(bstr2int(b'Hi!'), priv)
    >>> ciphertext
    2750689767
    >>> int2bstr(ciphertext)
    b'\xa3\xf41\xe7'

Then decrypt it using the public key:

    >>> plaintext = encrypt(ciphertext, pub)
    >>> int2bstr(plaintext)
    b'Hi!'

To encrypt a longer string, we have to break it up into chunks, encrypt each chunk separately, then concatenate
the chunks together to form the encrypted string. The chunk size should be no larger than the number of bits needed to represent the modulus. For example, if our modulus is 34 bits, chunks should be shorter than 34 bits. The resulting encrypted value will be 34 bits long, though. This poses a small problem: in addition to the encrypted chunks, we'll need to send the receiver additional information about the chunk size so they can chop up the byte string
appropriately.

Our encrypted string will include this additional information in a header.

* Byte 0: How long the header is (in bytes)
* Byte 1: The chunk size (in bytes)
* Byte 2: The encrypted value size (in bytes)
* Byte 3: The length of the final chunk (in bytes)

The rest of the encrypted data follows the header.

    >>> s = b'This is a test.'
    >>> len(s)
    15
    >>> enc = encrypt_str(s, pub)
    >>> enc
    b'\x04\x04\x05\x03\x01 \xe7\xff\xbd\x00\xd5M\x85\xff\x00,\xb2\xcbU\x00\xaf\x8f\x85\xbb'
    
The header says there are 4 bytes in the header, the plaintext was broken up into 4-byte chunks,
the ciphertext has 5-byte chunks, and the last plaintext chunk is 3 bytes long (because the length
of the plaintext is not a multiple of 4).

After encrypting, we can decrypt using decryptstr:

    >>> decrypt_str(enc, priv)
    b'This is a test.'

