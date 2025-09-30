def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma_digito1 = 0
    for i in range(9):
        numero = int(cpf[i])
        peso = 10 - i
        soma_digito1 += numero * peso
    resto_digito1 = (soma_digito1 * 10) % 11
    if resto_digito1 == 10:
        resto_digito1 = 0
    if resto_digito1 != int(cpf[9]):
        return False

    soma_digito2 = 0
    for i in range(10):
        numero = int(cpf[i])
        peso = 11 - i

        soma_digito2 += numero * peso
    resto_digito2 = (soma_digito2 * 10) % 11
    if resto_digito2 == 10:
        resto_digito2 = 0
    if resto_digito2 != int(cpf[10]):
        return False
    

    return True
