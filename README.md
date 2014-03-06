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

# Guides

* [Tutorial](TUTORIAL.md)
