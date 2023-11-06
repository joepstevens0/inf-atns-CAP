from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
ISSUER_MASTER_KEY = bytes.fromhex('01 23 45 67 89 AB CD EF 01 23 45 67 89 AB CD EF')
BLOCK_SIZE = 16


def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

def generate_master_key(primary_account_number: bytes, pan_seq_numb: bytes) -> bytes:
    Y = primary_account_number + pan_seq_numb
    Y_2 = byte_xor(Y,bytes.fromhex('FF FF FF FF FF FF FF FF'))

    cipher = AES.new(ISSUER_MASTER_KEY, AES.MODE_ECB)


    Zl = cipher.encrypt(pad(Y, BLOCK_SIZE) )
    Zr = cipher.encrypt(pad(Y_2, BLOCK_SIZE))

    master_key = Zl[0:8] + Zr[0:8]
    return master_key

def generate_session_key(primary_account_number: bytes, pan_seq_numb: bytes, ATC: bytes) -> bytes:
    MK = generate_master_key(primary_account_number, pan_seq_numb)
    R = ATC + bytes.fromhex('00 00 00 00 00 00 00 00 00 00 00 00 00 00')
    cipher = AES.new(MK, AES.MODE_ECB)
    session_key = cipher.encrypt(R)

    return session_key

print("test")
test_pan = bytes.fromhex('12 34 56 78 9A BC')
test_pan_seq_numb = bytes.fromhex('00 00')
test_atc = bytes.fromhex('00 01')
print(generate_session_key(test_pan, test_pan_seq_numb, test_atc).hex())