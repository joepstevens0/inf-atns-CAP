from Crypto.Hash import CMAC
from Crypto.Cipher import AES

from session_key import generate_session_key




class Card:
    pin: int
    atc: bytes # application transaction counter
    primary_account_number: bytes
    pan_seq_numb: bytes
    CAP_bit_filter: bytes
    
    def __init__(self) -> None:
        self.pin = 1234
        self.atc = bytes.fromhex("00 01")

        self.primary_account_number = bytes.fromhex('12 34 56 78 9A BC')
        self.pan_seq_numb = bytes.fromhex('00 00')
        self.atc = bytes.fromhex('00 01')

        self.CAP_bit_filter = bytes.fromhex('00 001F 0000000000000000 00000000000FFFFF 00000000008000')

    def get_CAP_bit_filter(self) -> bytes:
        return self.CAP_bit_filter
    
    def send_data(self, ):
        pass

    def checkModeSupported(self, mode: int) -> bool:
        return True

    def verifyPin(self, pin) -> bool:
        if(pin==self.pin):
            return True
        
        return False
    

    def generate_arqc(self, terminal_data) -> bytes:
        #Wat de kaart kan
        AIP = bytes.fromhex("78 00")

        data = b''
        data += terminal_data["amount"]
        data += terminal_data["amount_other"]
        data += terminal_data["country_code"]
        data += terminal_data["verification_results"]
        data += terminal_data["currency_code"]
        data += terminal_data["date"]
        data += terminal_data["type"]
        data += terminal_data["unpredictable_number"]
        data +=  AIP + self.atc


        session_key = generate_session_key(self.primary_account_number, self.pan_seq_numb, self.atc)
        cobj = CMAC.new(session_key, ciphermod=AES)
        cobj.update(data)
        AC = bytes.fromhex(cobj.hexdigest())
        CID = bytes.fromhex('80')
        ATC = self.atc
        IAD = bytes.fromhex('06 77 0A 03 A4 80 00')
        print("length of AC", len(AC), "  ", AC.hex())
        return CID + ATC + AC + IAD


    def generate_aac(self, terminal_data):
        pass

    def create_AC(self, terminal_data) -> bytes:
        # data = self.create_AC_data(terminal_data)
        return b''