from Crypto.PublicKey import RSA
import os

class RSACrypto:

    def __init__(self):
        self.keyPair = None

    def generateKeyPair(self):
        self.keyPair = RSA.generate(1024, os.urandom)

    def getNewRSAKey(self):
        # generate new RSA key
        self.generateKeyPair()
        # export keys
        key = {}
        key['public'] = RSAKey(self.keyPair.n, self.keyPair.e)
        key['private'] = RSAKey(self.keyPair.n, self.keyPair.d)
        return key


class RSAKey:

    def __init__(self, mod, exp):
        self.mod = mod
        self.exp = exp
  