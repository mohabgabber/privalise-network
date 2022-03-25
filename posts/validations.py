import gpg
import os
from cryptography.fernet import Fernet 

# GPG

c = gpg.Context(armor=True)
c.home_dir = os.path.expanduser("~/.gnupg")
def valid_sig(signature, username, author, pk):
    try:
       msg = c.verify(open(f'signatures/{username}+{author}+{pk}.txt'))
       os.remove(f'signatures/{username}+{author}+{pk}.txt')
       return True
    except:
       os.remove(f'signatures/{username}+{author}+{pk}.txt')
       return False
def gpgkeyimport(ssss):
    try: 
        result = c.key_import(ssss)
        fingerprint = str(result.imports[0].fpr)
        return fingerprint
    except:
        return False