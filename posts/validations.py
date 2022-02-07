import gpg
import os
from monero.wallet import Wallet
from decimal import Decimal
from monero.address import address
from cryptography.fernet import Fernet 

c = gpg.Context()
w = Wallet(port=28088)
def create_addr():
    new_addr = w.new_address()
    return new_addr
def pay(addr, amnt):
    monero = address(addr)
    if monero:
        tx = w.transfer(addr, Decimal(str(amnt)))
        return tx
    else:
        return False
def receive(amnt, addr, hashes):
    incoming = w.incoming(local_address=addr, unconfirmed=True, confirmed=True)
    if float(amnt) >= 0.004:
        if incoming[0] and float(incoming[0].amount) >= float(amnt) and incoming[0].transaction.hash == hashes and incoming[0].local_address == addr:
            return True
        else:
            return False
    else:
        return False
def check_addr(addr):
    incoming = w.incoming(local_address=addr, unconfirmed=True, confirmed=True)
    try: 
        tx = incoming[0]
        return False
    except:
        return True
def check_conf_number(addr, hash, amnt):
    tx = w.incoming(local_address=addr, unconfirmed=True, confirmed=True)
    confs = w.confirmations(tx[0])
    return confs
def check_conf(addr, hash, amnt):
    tx = w.incoming(local_address=addr, unconfirmed=True, confirmed=True)
    confs = w.confirmations(tx[0])
    if confs >= 5:
        return True
    else:
        return False
def valid_sig(signature, username, author, pk):
    try:
       msg = c.verify(open(f'signatures/{username}+{author}+{pk}.txt'))
       os.remove(f'signatures/{username}+{author}+{pk}.txt')
       return True
    except:
       os.remove(f'signatures/{username}+{author}+{pk}.txt')
       return False
def valid_addr(addr):
    try:
        monero = address(addr)
        return True
    except:
        return False


import base64
from cryptography.exceptions import AlreadyFinalized
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from rsa.key import PrivateKey
def encryption_decryption(text, password, ed):
    password_bytes = password.encode('utf-8')
    salt = b"I\x84\xa0\x1bkg\xef,\x1b\xfb\xc9\xaf:\xb8'#\x92C0\xbaI\xab\xe6\x94^v+e\x96\xad\x1e\xccBg\xa1\xa2\x82\xe98HU\xb1v\x08\xb7\xea<\xc0\xb5\x0c\xc1\xaa\xea\xa4\xe9\xfb\xba\xc0A\xfd\x10\x99\x9d\x03"
    kdf = PBKDF2HMAC(algorithm=hashes.SHA512(), length=32, salt=salt, iterations=10000, backend=default_backend())
    key = kdf.derive(password_bytes)
    nonce = b'\xaf\xfa\xed9\xb1\xd1\xc1N\xb1\x1c95'
    aesgcm = AESGCM(key)
    try:   
        if ed == 'e':   
            cipher_text_bytes = aesgcm.encrypt(nonce=nonce, data=text.encode('utf-8'), associated_data=None)
            cipher_text = base64.urlsafe_b64encode(cipher_text_bytes)
            return cipher_text
        elif ed == 'd':
            decrypted_cipher_text_bytes = aesgcm.decrypt(nonce=nonce, data=base64.urlsafe_b64decode(text), associated_data=None)
            decrypted_cipher_text = decrypted_cipher_text_bytes.decode('utf-8')
            return decrypted_cipher_text
    except:
        return False 

