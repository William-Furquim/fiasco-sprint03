# utils.py
from datetime import datetime

def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma_digito1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto_digito1 = (soma_digito1 * 10) % 11
    if resto_digito1 == 10:
        resto_digito1 = 0
    if resto_digito1 != int(cpf[9]):
        return False

    soma_digito2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto_digito2 = (soma_digito2 * 10) % 11
    if resto_digito2 == 10:
        resto_digito2 = 0
    if resto_digito2 != int(cpf[10]):
        return False

    return True

def validar_data(data_str, formato="%d/%m/%Y"):
    try:
        datetime.strptime(data_str, formato)
        return True
    except ValueError:
        return False