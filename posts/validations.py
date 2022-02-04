import gpg
import os
from monero.wallet import Wallet
from decimal import Decimal
from monero.address import address
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
