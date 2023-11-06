from Crypto.Hash import CMAC
from Crypto.Cipher import AES

from session_key import generate_session_key
import random


CAP_bit_filter = bytes.fromhex('00 001F 0000000000000000 00000000000FFFFF 00000000008000')
TOTAL_RESPONSE_BITS = 26
CARD_DATABASE = {
    bytes.fromhex("12 34 56 78 9A BC 00 00") : {
        "last_atc": bytes.fromhex("00 00"),
        "pin": bytes.fromhex("1234"),
        "verification_results": bytes.fromhex("08 00 00 00 00")
    }
}

def apply_bit_filter(arqc: bytes, filter: bytes) -> int:
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

def generate_arqc(terminal_data, atc, primary_account_number, pan_seq_numb) -> bytes:
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
    data +=  AIP + atc


    session_key = generate_session_key(primary_account_number, pan_seq_numb, atc)
    cobj = CMAC.new(session_key, ciphermod=AES)
    cobj.update(data)
    AC = bytes.fromhex(cobj.hexdigest())
    CID = bytes.fromhex('80')
    ATC = atc
    IAD = bytes.fromhex('06 77 0A 03 A4 80 00')
    print("length of AC", len(AC), "  ", AC.hex())
    return CID + ATC + AC + IAD

def calc_atc_from_response(response: int, primary_account_number: bytes, pan_seq_numb: bytes)->  bytes:
    response_bytes = bin(response)[2:]
    while len(response_bytes) < TOTAL_RESPONSE_BITS:
        response_bytes = '0' + response_bytes

    atc_least_significant = response_bytes[0:5]
    atc_most_significant = bin(int(CARD_DATABASE[primary_account_number + pan_seq_numb]["last_atc"].hex(), base=16))[2:][0:11]

    atc = int(atc_most_significant + atc_least_significant, base=2).to_bytes(2, 'big')
    
    return atc

def generate_challenge() -> bytes:
    return random.randint(0,99999999).to_bytes(4, byteorder='big')

def verify_response(response: int, primary_account_number, pan_seq_numb, challenge: bytes = bytes.fromhex("00 00 00 00"), amount:bytes = bytes.fromhex("00 00 00 00 00 00"), amount_other:bytes = bytes.fromhex("00 00 00 00 00 00")) -> bool:
    # create terminal data
    terminal_data = {}
    terminal_data["amount"] = amount
    terminal_data["amount_other"] = amount_other
    terminal_data["country_code"] = bytes.fromhex("00 56")
    terminal_data["verification_results"] = bytes.fromhex("08 00 00 00 00")
    terminal_data["currency_code"] = bytes.fromhex("09 78")
    terminal_data["date"] = bytes.fromhex("28 02 00")
    terminal_data["type"] = bytes.fromhex("01")
    terminal_data["unpredictable_number"] = challenge

    atc = calc_atc_from_response(response, primary_account_number, pan_seq_numb)

    expected_arqc = generate_arqc(terminal_data, atc, primary_account_number, pan_seq_numb)

    expected_response = apply_bit_filter(expected_arqc, CAP_bit_filter)

    return response == expected_response



def ask_application() -> int:
    answer = input("Select mode: sign(1) identify(2) respond(3): ")
    return int(answer)

def start_respond():
    primary_account_number = input("Enter primary account number")
    pan_seq_numb = input("Enter pan seq numb")
    challenge = generate_challenge()
    print("Challenge: ", int(challenge.hex(), base=16))

    response = input("Input response")

    if verify_response(int(response), bytes.fromhex(primary_account_number), bytes.fromhex(pan_seq_numb), challenge):
        print("Success")
    else:
        print("Fail")

    

def start_sign():
    primary_account_number = input("Enter primary account number (6 bytes)")
    pan_seq_numb = input("Enter pan seq numb (2 bytes)")
    challenge = generate_challenge()
    print("Challenge: ",  int(challenge.hex(), base=16))
    amount = int(input("Enter amount (10 numbers)")).to_bytes(6, byteorder='big')
    print("amount: ", amount)

    response = input("Input response")

    if verify_response(int(response), bytes.fromhex(primary_account_number), bytes.fromhex(pan_seq_numb), challenge, amount):
        print("Success")
    else:
        print("Fail")

def start_identify():
    primary_account_number = input("Enter primary account number")
    pan_seq_numb = input("Enter pan seq numb")

    response = input("Input response")

    if verify_response(int(response), bytes.fromhex(primary_account_number), bytes.fromhex(pan_seq_numb)):
        print("Success")
    else:
        print("Fail")
    

def choose_mode():
    # ask mode
    mode = ask_application()

    # ask pin
    if(mode == 1):
        start_sign()
    elif(mode == 2):
        start_identify()
    elif(mode == 3):
        start_respond()


choose_mode()