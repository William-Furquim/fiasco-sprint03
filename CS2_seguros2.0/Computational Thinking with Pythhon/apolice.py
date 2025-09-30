# apolice.py - Versão Final com Exceções, Logs e Correção de Erro
import uuid
import os
import time
import dao 
from excecoes import DadoInexistente, ApoliceInativa, RegraNegocioViolada
from logs import logging 

class Apolice:
    def __init__(self, numero, cliente_cpf, seguro_id, valor_mensal, ativa=True):
        self.numero = numero
        self.cliente_cpf = cliente_cpf
        self.seguro_id = seguro_id
        self.valor_mensal = float(valor_mensal)
        self.ativa = ativa

    def cancelar(self):
        if not self.ativa:
            raise ApoliceInativa(f"Apólice {self.numero} já está inativa.")

        self.ativa = False
        dao.atualizar_status_apolice(self.numero, False)

    def to_dict(self):
        return self.__dict__

def emitir_apolice(sistema):
    os.system("cls")
    print("|---------------------=<@>=---------------------|")
    print("              Emissão de Nova Apólice              \n")
    
    clientes_disponiveis = dao.buscar_todos_clientes()
    seguros_disponiveis = dao.buscar_todos_seguros()
    
    numero_nova_apolice = None
    cpf_cliente = None
    
    try:
        if not clientes_disponiveis:
            raise DadoInexistente("Nenhum cliente cadastrado.")
        if not seguros_disponiveis:
            raise DadoInexistente("Nenhum tipo de seguro cadastrado.")

        cpf_cliente = input("CPF do cliente para a apólice: ")
        cliente_obj = dao.buscar_cliente_por_cpf(cpf_cliente)
        if not cliente_obj:
            raise DadoInexistente("Cliente não encontrado.")

        print("\nSeguros disponíveis para contratação:")
        for indice, seguro_disp in enumerate(seguros_disponiveis):
            detalhe = f"{indice+1}. ID: {seguro_disp.id}, Tipo: {seguro_disp.tipo}, Valor Base: R$ {seguro_disp.valor:.2f}"
            print(detalhe)
        
        # --- CORREÇÃO: Inicializa 'escolha' e move a validação para o bloco principal ---
        escolha = None
        escolha_str = input("Escolha o número do seguro desejado: ")
        
        if not escolha_str.isdigit():
            raise RegraNegocioViolada("Entrada inválida. Por favor, digite um número.")
            
        escolha = int(escolha_str) - 1
        
        if not (0 <= escolha < len(seguros_disponiveis)):
            raise DadoInexistente("Opção de seguro inválida.")
        # ---------------------------------------------------------------------------------

        seguro_escolhido = seguros_disponiveis[escolha]
        
        valor_mensal_apolice = seguro_escolhido.valor * 0.05
        numero_nova_apolice = "AP-" + str(uuid.uuid4())[:8].upper()

        nova_apolice = Apolice(numero_nova_apolice, cpf_cliente, seguro_escolhido.id, valor_mensal_apolice)
        dao.inserir_apolice(nova_apolice)
        
        # Log de sucesso
        sistema.registrar_log_operacao(
            logging.INFO, 
            f"APÓLICE EMITIDA. Nº: {numero_nova_apolice}, Cliente CPF: {cpf_cliente}, Tipo: {seguro_escolhido.tipo}."
        )
        
        print(f"\nApólice '{numero_nova_apolice}' emitida com sucesso para o cliente '{cliente_obj.nome}'!")
        print(f"Valor mensal: R$ {valor_mensal_apolice:.2f}")

    except (DadoInexistente, RegraNegocioViolada) as e:
        sistema.registrar_log_operacao(logging.WARNING, f"TENTATIVA DE EMISSÃO FALHA. Motivo: {e}")
        print(f"\nERRO: {e}")
    except Exception as e:
        sistema.registrar_log_operacao(logging.ERROR, f"ERRO INESPERADO na emissão de apólice: {e}")
        print(f"\nOcorreu um erro inesperado: {e}")
        
    time.sleep(4)


def listar_apolices_ativas(sistema):
    os.system("cls")
    print("|---------------------=<@>=---------------------|")
    print("                Apólices Ativas                \n")
    
    apolices = dao.buscar_todas_apolices()
    apolices_ativas_encontradas = False
    
    for ap in apolices:
        if ap.ativa:
            cliente_nome = "Desconhecido"
            cliente_obj = dao.buscar_cliente_por_cpf(ap.cliente_cpf)
            if cliente_obj:
                cliente_nome = cliente_obj.nome
            
            print(f"| Número: {ap.numero}")
            print(f"| Cliente: {cliente_nome} (CPF: {ap.cliente_cpf})")
            print(f"| Seguro ID: {ap.seguro_id}")
            print(f"| Mensal: R$ {ap.valor_mensal:.2f}")
            print("|--------------------------")
            apolices_ativas_encontradas = True
    
    if not apolices_ativas_encontradas:
        print("Nenhuma apólice ativa encontrada no sistema.")        
    input("\nPressione Enter para retornar ao menu...")


def cancelar_apolice(sistema):
    os.system("cls")
    print("|---------------------=<@>=---------------------|")
    print("              Cancelamento de Apólice              \n")
    
    numero_apolice = None
    try:
        numero_apolice = input("Número da apólice: ")
        apolice = dao.buscar_apolice_por_numero(numero_apolice)
        
        if not apolice:
            raise DadoInexistente("Apólice não encontrada.")
        
        confirmacao = input(f"Confirma o cancelamento da apólice {numero_apolice}? (s/n): ").lower()
        if confirmacao == 's':
            apolice.cancelar()
            
            # Log de sucesso
            sistema.registrar_log_operacao(logging.INFO, f"APÓLICE CANCELADA. Nº: {numero_apolice}.")
            
            print("Apólice cancelada com sucesso!")
        else:
            print("Cancelamento abortado.")
            
    except DadoInexistente as e:
        sistema.registrar_log_operacao(logging.WARNING, f"TENTATIVA DE CANCELAMENTO FALHA. Apólice não encontrada: {numero_apolice}.")
        print(f"\nERRO: {e}")
    except ApoliceInativa as e:
        sistema.registrar_log_operacao(logging.WARNING, f"TENTATIVA DE CANCELAMENTO FALHA. Apólice já inativa: {numero_apolice}.")
        print(f"\nERRO: {e}")
    except Exception as e:
        sistema.registrar_log_operacao(logging.ERROR, f"ERRO INESPERADO no cancelamento de apólice: {e}")
        print(f"\nOcorreu um erro inesperado: {e}")
        
    time.sleep(3)