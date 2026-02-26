import re

def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D+", "", phone or "")
    if len(digits) < 10 or len(digits) > 15:
        raise ValueError("Invalid phone number length")
    return digits

def validate_snils(snils: str) -> str:
    digits = re.sub(r"\D+", "", snils or "")
    if not digits:
        return digits
    if len(digits) != 11:
        raise ValueError("SNILS must contain 11 digits")

    number = digits[:9]
    checksum = int(digits[9:])

    s = sum(int(number[i]) * (9 - i) for i in range(9))
    if s < 100:
        calc = s
    elif s in (100, 101):
        calc = 0
    else:
        calc = s % 101
        if calc == 100:
            calc = 0

    if checksum != calc:
        raise ValueError("Invalid SNILS checksum")

    return digits