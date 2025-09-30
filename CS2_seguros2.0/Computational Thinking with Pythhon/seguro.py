# seguro.py - VERSÃO À PROVA DE FALHAS DE HERANÇA
import uuid
import os
import time
import dao 

class Seguro:
    # 1. O construtor aceita *qualquer* argumento extra (**kwargs) e o ignora.
    def __init__(self, tipo, valor, id=None, *args, **kwargs): 
        self.id = id if id else str(uuid.uuid4())
        self.tipo = tipo
        self.valor = float(valor)

    @classmethod
    def from_dict(cls, data):
        # 1. Pega o ID, TIPO e VALOR (chaves da superclasse) e remove elas do dicionário
        seguro_id = data.pop('id', None)
        tipo = data.pop('tipo', None)
        valor = data.pop('valor', 0.0) 
        
        # O dicionário 'data' agora contém APENAS os campos específicos (beneficiarios, endereco_imovel, etc.)
        
        # 2. Instancia a subclasse, passando o ID, VALOR, e o resto via **data.
        #    Graças à correção no __init__, ele não vai reclamar de chaves extras.
        if tipo == "Automóvel":
            return Automovel(id=seguro_id, valor=valor, **data) 
        elif tipo == "Residencial":
            return Residencial(id=seguro_id, valor=valor, **data)
        elif tipo == "Vida":
            return Vida(id=seguro_id, valor=valor, **data)
            
        # Fallback
        return cls(id=seguro_id, valor=valor, tipo=tipo, **data)
        
    def to_dict(self):
        return self.__dict__
        
class Automovel(Seguro):
    # Aceita os argumentos definidos e *qualquer* argumento extra da **superclasse**
    def __init__(self, valor, modelo=None, ano=None, placa=None, id=None, *args, **kwargs):
        super().__init__("Automóvel", valor, id, *args, **kwargs)
        self.modelo = modelo
        self.ano = ano
        self.placa = placa

class Residencial(Seguro):
    # Aceita os argumentos definidos e *qualquer* argumento extra da **superclasse**
    def __init__(self, valor, endereco_imovel=None, id=None, *args, **kwargs):
        super().__init__("Residencial", valor, id, *args, **kwargs)
        self.endereco_imovel = endereco_imovel

class Vida(Seguro):
    # Aceita os argumentos definidos e *qualquer* argumento extra da **superclasse**
    def __init__(self, valor, beneficiarios=None, id=None, *args, **kwargs):
        super().__init__("Vida", valor, id, *args, **kwargs)
        self.beneficiarios = beneficiarios

# ... (O restante do código cadastrar_seguro permanece inalterado) ...
def cadastrar_seguro(sistema):
    os.system("cls")
    print("|---------------------=<@>=---------------------|")
    print("    Cadastro de Novo Seguro (Modelo/Produto)    \n")
    print("Tipos de seguro disponíveis: 1. Automóvel, 2. Residencial, 3. Vida")
    tipo_escolha = input("Escolha o tipo de seguro (1, 2 ou 3): ")

    if tipo_escolha == '1':
        modelo = input("Modelo do automóvel: ")
        ano = input("Ano do automóvel: ")
        placa = input("Placa do automóvel: ")
        try:
            valor = float(input("Valor do veículo: "))
        except ValueError:
            print("Valor inválido. Definido como R$0.00.")
            valor = 0.0
        novo_seguro = Automovel(valor, modelo, ano, placa)
    elif tipo_escolha == '2':
        endereco_imovel = input("Endereço do imóvel segurado: ")
        try:
            valor = float(input("Valor do imóvel: "))
        except ValueError:
            print("Valor inválido. Definido como R$0.00.")
            valor = 0.0
        novo_seguro = Residencial(valor, endereco_imovel)
    elif tipo_escolha == '3':
        try:
            valor = float(input("Valor segurado (vida R$): "))
        except ValueError:
            print("Valor inválido. Definido como R$0.00.")
            valor = 0.0
        beneficiarios = input("Beneficiários (separe por vírgula, se houver mais de um): ")
        novo_seguro = Vida(valor, beneficiarios)
    else:
        print("Tipo de seguro inválido.")
        time.sleep(3)
        return

    dao.inserir_seguro(novo_seguro)
    print(f"\nSeguro tipo '{novo_seguro.tipo}' (ID: {novo_seguro.id}) cadastrado com sucesso!")
    time.sleep(3)