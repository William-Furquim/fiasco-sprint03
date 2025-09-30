# cliente.py - Versão com Exceções e Logs de Auditoria

import os
import time
from utils import validar_cpf 
import dao 
from excecoes import DadoJaExiste, RegraNegocioViolada, DadoInexistente
from logs import logging # Importa o logging para usar os níveis INFO/WARNING

class Cliente:
# ... (Classe Cliente permanece inalterada) ...
    def __init__(self, cpf, nome, data_nasc, endereco, telefone, email):
        self.cpf = cpf
        self.nome = nome
        self.data_nasc = data_nasc
        self.endereco = endereco
        self.telefone = telefone
        self.email = email

    def atualizar_dados(self, telefone=None, email=None):
        if telefone:
            self.telefone = telefone
        if email:
            self.email = email
            
    def to_dict(self):
        return self.__dict__


def cadastrar_cliente(sistema):
    os.system("cls")
    print("|---------------------=<@>=---------------------|")
    print("             Cadastro de Novo Cliente             \n")
    
    cpf_input = None
    try:
        cpf_input = input("CPF (apenas números): ")
        if not validar_cpf(cpf_input):
            raise RegraNegocioViolada("CPF inválido ou formato incorreto!")

        if dao.buscar_cliente_por_cpf(cpf_input):
            raise DadoJaExiste(f"Cliente com CPF {cpf_input} já está cadastrado.")
            
        nome = input("Nome completo: ")
        data_nascimento = input("Data de Nascimento (DD/MM/AAAA): ")
        
        try:
            from datetime import datetime
            datetime.strptime(data_nascimento, "%d/%m/%Y")
        except ValueError:
            raise RegraNegocioViolada("Data de nascimento inválida (formato: DD/MM/AAAA).")

        endereco = input("Endereço: ")
        telefone = input("Telefone: ")
        email = input("E-mail: ")

        if not nome or not endereco:
            raise RegraNegocioViolada("Nome e endereço são obrigatórios!")

        novo_cliente = Cliente(cpf=cpf_input, nome=nome, data_nasc=data_nascimento, endereco=endereco, telefone=telefone, email=email)
        
        dao.inserir_cliente(novo_cliente)
        
        # Log de sucesso
        sistema.registrar_log_operacao(
            logging.INFO, 
            f"CLIENTE CADASTRADO. Nome: {nome}, CPF: {cpf_input}."
        )
        
        print(f"\nCliente '{nome}' cadastrado com sucesso!")
        
    except RegraNegocioViolada as e:
        sistema.registrar_log_operacao(
            logging.WARNING, 
            f"TENTATIVA DE CADASTRO FALHA. Motivo: {e}"
        )
        print(f"\nERRO DE VALIDAÇÃO: {e}")
    except DadoJaExiste as e:
        sistema.registrar_log_operacao(
            logging.WARNING, 
            f"TENTATIVA DE CADASTRO FALHA. CPF duplicado: {cpf_input}."
        )
        print(f"\nERRO: {e}")
    except Exception as e:
        sistema.registrar_log_operacao(logging.ERROR, f"ERRO INESPERADO no cadastro de cliente: {e}")
        print(f"\nOcorreu um erro inesperado: {e}")

    time.sleep(3)


def editar_cliente(sistema):
    os.system("cls")
    print("|---------------------=<@>=---------------------|")
    print("             Editar Cliente             \n")
    
    cpf_input = None
    try:
        cpf_input = input("CPF do cliente: ")
        
        cliente_obj = dao.buscar_cliente_por_cpf(cpf_input) 
        
        if not cliente_obj:
            raise DadoInexistente(f"Cliente com CPF {cpf_input} não encontrado.")

        print(f"Cliente: {cliente_obj.nome}")
        telefone = input("Novo telefone (deixe vazio para manter): ")
        email = input("Novo e-mail (deixe vazio para manter): ")

        cliente_obj.atualizar_dados(telefone, email)
        
        dao.atualizar_cliente(cliente_obj)
        
        # Log de sucesso
        sistema.registrar_log_operacao(
            logging.INFO, 
            f"CLIENTE EDITADO. CPF: {cpf_input}, Contatos atualizados."
        )
        
        print("\nDados atualizados com sucesso!")
        
    except DadoInexistente as e:
        sistema.registrar_log_operacao(
            logging.WARNING, 
            f"TENTATIVA DE EDIÇÃO FALHA. Cliente não encontrado: {cpf_input}."
        )
        print(f"\nERRO: {e}")
    except Exception as e:
        sistema.registrar_log_operacao(logging.ERROR, f"ERRO INESPERADO na edição de cliente: {e}")
        print(f"\nOcorreu um erro inesperado: {e}")
        
    time.sleep(3)