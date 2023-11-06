from card import Card

from Crypto.Hash import CMAC
from Crypto.Cipher import AES

class Readers:
    def __init__(self) -> None:
        pass


    def start(self):
        # insert card
        cardNumber = input("Press any enter to insert card")

        #Temp 
        card = Card()

        # ask mode
        mode = self.ask_application()
        if not card.checkModeSupported(mode):
            print("Mode not supported")
            return

        # ask pin
        pinVerifed = self.verify_pin(card)
        if(pinVerifed):
            if(mode == 1):
                self.start_sign(card)
            elif(mode == 2):
                self.start_identify(card)
            elif(mode == 3):
                self.start_respond(card)
        else:
            print("FAILED TO UNLOCK CARD, YOU LOSER")
        
    

    def ask_application(self) -> int:
        answer = input("Select mode: sign(1) identify(2) respond(3): ")
        return int(answer)
        
    def ask_pin(self) -> int:
        answer = input("Enter pin: ")
        return int(answer)
    
    def ask_challenge(self) -> bytes:
        answer = input("Enter challenge (8 numbers): ")
        return int(answer).to_bytes(4, byteorder='big')
    
    def ask_amount(self) -> bytes:
        answer = input("Enter amount (6 bytes): ")
        return bytes.fromhex(answer)

    def read_pin(self) -> int:
        # TODO
        return 1234

   

    def verify_pin(self, card: Card) -> bool:
        
        for _ in range(0,3):
            pin = self.ask_pin()
            if card.verifyPin(pin):
                print("PIN Correct!!!")
                return True
            print("Retry PIN")
        return False
        
    def start_identify(self, card: Card) -> None:
        
        arqc = self.generate_arqc(card)
        if not self.verify_arqc(arqc):
            print("ARQC generation failed")
            return

        response = self.apply_bit_filter(arqc, card.get_CAP_bit_filter())

        print("Reponse: " + str(response))
        
        aac = self.generate_aac(card)
        # TODO verify aac


    def verify_arqc(self, arqc: bytes) -> bool:
        return True
    
    def apply_bit_filter(self, arqc: bytes, filter: bytes) -> int:
        total_shifts = 0

        result = 0
        arqc_bits = int.from_bytes(arqc, "big")
        filter_bits = int.from_bytes(filter, "big")
        while filter_bits > 0:
            if filter_bits & 1:
                if arqc_bits & 1:
                    result |= 1
                result = result << 1
                total_shifts += 1


            filter_bits = filter_bits >> 1
            arqc_bits = arqc_bits >> 1

        # reverse response
        r = 0
        for _ in range(0, total_shifts):
            if result & 1:
                r |= 1
            r = r << 1
            result = result >> 1

        if result & 1:
            r |= 1

        return r
            
        
    def start_respond(self, card: Card) -> None:
        # ask for the challenge
        challengeValue = self.ask_challenge()
        
        arqc = self.generate_arqc(card, challengeValue)
        if not self.verify_arqc(arqc):
            print("ARQC generation failed")
            return

        response = self.apply_bit_filter(arqc, card.get_CAP_bit_filter())

        print("Reponse: " + str(response))
        
        aac = self.generate_aac(card, challengeValue)
        # TODO verify aac

    def start_sign(self, card: Card) -> None:
        # ask for the challenge
        challengeValue = self.ask_challenge()

        # ask for amount
        amount = self.ask_amount()
        
        arqc = self.generate_arqc(card, challengeValue, amount)
        if not self.verify_arqc(arqc):
            print("ARQC generation failed")
            return

        response = self.apply_bit_filter(arqc, card.get_CAP_bit_filter())

        print("Reponse: " + str(response))
        
        aac = self.generate_aac(card, challengeValue)
        # TODO verify aac



    def generate_arqc_data(self, challenge = 0, amount = 0, amountCurrency = 0):
        result = {}


        result["amount"] = amount # amount is 0 for identify

        return result

    def generate_arqc(self, card: Card, challenge: bytes = bytes.fromhex('00 00 00 00'), amount: bytes = bytes.fromhex('00 00 00 00 00 00')) -> bytes:
        # create terminal data
        terminal_data = {}
        terminal_data["amount"] = amount
        terminal_data["amount_other"] = bytes.fromhex("00 00 00 00 00 00")
        terminal_data["country_code"] = bytes.fromhex("00 56")
        terminal_data["verification_results"] = bytes.fromhex("08 00 00 00 00")
        terminal_data["currency_code"] = bytes.fromhex("09 78")
        terminal_data["date"] = bytes.fromhex("28 02 00")
        terminal_data["type"] = bytes.fromhex("01")
        terminal_data["unpredictable_number"] = challenge

        arqc = card.generate_arqc(terminal_data)

        return arqc
    
    def generate_aac(self, card: Card, challenge: bytes = bytes.fromhex('00 00 00 00')) -> bytes:
        pass # TODO
        return b'0000'


reader = Readers()
reader.start()
