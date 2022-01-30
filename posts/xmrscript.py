from monero.wallet import Wallet
from decimal import Decimal
from monero.address import address

w = Wallet(port=28088)

def create_addr(id):
    new_addr = w.new_address(label=id)
    return new_addr
def pay(addr, amnt):
    addr = address(addr)
    if addr:
        tx = w.transfer(addr, Decimal(str(amnt)))
        return tx
    else:
        return False
def receive(amnt, addr, hash):
    incoming = w.incoming(local_address=addr, unconfirmed=True, confirmed=True)
    if incoming and incoming.amount == amnt and incoming.transaction.hash == hash and incoming.local_address == addr:
        return True
    else:
        return False
def check_addr(addr):
    incoming = w.incoming(local_address=addr)
    if incoming[0]:
        return False
    else:
        return True
def check_conf(addr, hash, amnt):
    tx = w.incoming(local_address=addr)
    if tx.amount == amnt and tx.transaction.hash == hash and tx.local_address == addr:
        confs = w.confirmations(tx)
        if confs >= 5:
            return True
        else:
            return False
    else:
        return False

