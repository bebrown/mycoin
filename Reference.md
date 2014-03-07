# Reference

### Data formats

Most data is represented with ints or byte strings. Typically, functions default to input/output
using byte strings. In rare cases, regular strings are used.

Composite data structures include lists, tuples, and dictionaries.

No classes or objects are used.

### Conversion / Formatting

##### bstr2int(bstr)

Convert a byte string to an integer. No zero-padding is performed.

##### int2bstr(int)

Convert an integer to a byte string. No zero-padding is performed.

##### to_base64(bstr)

Encode a byte string using base64. Returns a byte string.

##### from_base64(bstr)

Decode a base64 string into a byte string.

##### md5(data, bytes=16)

Return the MD5 hash of the given data (a byte string). Defaults to the full size of the MD5 hash,
16 bytes. The size of the hash can be reduced. For example, the user might want a hash that is
only 4 bytes long. When this happens, only the lower n bytes of the hash are returned.

##### to_base58(data)

Encode a byte string using base58, similar to the Bitcoin address format.

##### serialize(arr)

Serialize an array of byte strings, returning a single byte string.

Individual elements of the array can be arbitrarily-sized; the encoding supports it.
The encoding is simple: each element of the array is prefixed with the size of the element.
For example, the string b'hello' would be encoded as b'\x05hello'. Strings longer than 255
characters get a two-byte prefix. Strings longer than 65,535 bytes have a three-byte
prefix, and so on. All elements of the array, regardless of their actual size, will get the
same-sized prefix, depending on the length of the longest element.

Elements and their prefixes are simply concatenated together. The entire string gets its
own one-byte prefix indicating how long the element prefixes are.

The array `[b'Hello', b'World!']` is thusly encoded as `b'\x01\x05Hello\x06World!'`

##### deserialize(bstr)

Reverse the serialization process. Returns an array of byte strings.

### RSA Encryption

##### genkeys(p, q)

Given two primes numbers, p and q, return a tuple of the generated keys. Each key itself is a
tuple of the exponent and modulus, serialized into an integer.

##### key_decode(key)

The given key (assumed to be encoded as a serialized integer) is decoded into its components:
the exponent and modulus. They are returned as a tuple.

##### key_encode(exp, modulus)

Encode an (exponent, modulus) pair into a serialized integer.

##### encrypt(data, key)

Encrypt a blob of data (a byte string) using the given key. The data must be shorter (bitwise)
than the modulus. Error checking is not performed.

##### encrypt_str(bstr, key)

Encrypt a longer string using the given key. The string is broken up into chunks, appropriately
sized according to the magnitude of the modulus, individually encrypted, and the results
concatenated together. Each output chunk may be longer than the input chunks, due to the
modulus.

The entire string is prefixed with a header consisting of four bytes:

* Byte 1: The length of the header, 0x04
* Byte 2: The length of each input chunk
* Byte 3: The length of each output chunk
* Byte 4: The length of the final input chunk, because the original string length may not
  be a multiple of the input chunk size.

##### decrypt_str(bstr, key)

Decrypt a string using the given key. Assumes the encrypted string has the four-byte header
as described above.

### Signing

##### make_signature(message, key)

Generate an encrypted hash of a message using the given key.

##### sign(message, key)

Attach a signature to a message using the given key. The message and signature
are serialized and the resulting byte string is returned.

##### verify_signature(signed_message, key)

Given a signed message, verify the signature by comparing hashes. Returns True or False.

### Coin Protocol

##### my_address(pub_key)

Given a key (should be the public key), hash it and encode it in base58. Returns an
address similar to the ones used by Bitcoin.
