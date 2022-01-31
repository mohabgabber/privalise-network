#import gpg
import os

#c = gpg.Context()
'''
from monero.wallet import Wallet
from decimal import Decimal
from monero.address import address

w = Wallet(port=28088)

def create_addr(id):
    new_addr = w.new_address(label=id)
    return new_addr
def pay(addr, amnt):
    monero = address(addr)
    if monero:
        tx = w.transfer(addr, Decimal(str(amnt)))
        return tx
    else:
        return False
def valid_addr(addr):
    try:
        monero = address(addr)
        return True
    except:
        return False
def receive(amnt, addr, hashes):
    incoming = w.incoming(local_address=addr, unconfirmed=True, confirmed=True)
    if incoming[0] and float(incoming[0].amount) >= float(amnt) and incoming[0].transaction.hash == hashes and incoming[0].local_address == addr:
        return True
    else:
        return False
def check_addr(addr):
    incoming = w.incoming(local_address=addr, unconfirmed=True, confirmed=True)
    if incoming[0]:
        return False
    else:
        return True
def check_conf(addr, hash, amnt):
    tx = w.incoming(local_address=addr, unconfirmed=True, confirmed=True)
    confs = w.confirmations(tx[0])
    if confs >= 5:
        return True
    else:
        return False

def valid_sig(signature, id):
    sig = open(f'signatures/{id}.txt', 'w')
    sig.write(signature)
    f.close()
    try:
       msg = c.verify(sig)
       os.remove(f'signatures/{id}.txt')
       return True
    except:
       os.remove(f'signatures/{id}.txt')
       return False
'''
