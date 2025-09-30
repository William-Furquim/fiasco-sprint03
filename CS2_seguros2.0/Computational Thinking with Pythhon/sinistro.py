# sinistro.py - Versão Final com Exceções, Logs e Correção de Erro
import datetime
import time
import os
import dao 
from excecoes import DadoInexistente, ApoliceInativa, RegraNegocioViolada
from logs import logging 

class Sinistro:
    def __init__(self, cliente_cpf, numero_apolice, descricao, data, status, id=None): 
        self.id = id 
        self.cliente_cpf = cliente_cpf
        self.numero_apolice = numero_apolice
        self.descricao = descricao
        self.data = data
        self.status = status

    def atualizar_status(self, novo_status):
        if novo_status not in ["aberto", "fechado"]:
            raise RegraNegocioViolada("Status inválido. Use 'aberto' ou 'fechado'.")
            
        self.status = novo_status
        dao.atualizar_status_sinistro(self.id, novo_status) 

    def to_dict(self):
        return self.__dict__

def registrar_sinistro(sistema):
    os.system("cls")
    print("|---------------------=<@>=---------------------|")
    print("            Registro de Novo Sinistro            \n")
    
    apolices_disponiveis = dao.buscar_todas_apolices()
    numero_apolice_input = None
    
    try:
        if not apolices_disponiveis:
            raise DadoInexistente("Nenhuma apólice emitida para registrar sinistro.")

        numero_apolice_input = input("Número da apólice: ")
        apolice_encontrada = dao.buscar_apolice_por_numero(numero_apolice_input)

        if not apolice_encontrada:
            raise DadoInexistente(f"Apólice '{numero_apolice_input}' não encontrada.")

        if not apolice_encontrada.ativa:
            raise ApoliceInativa(f"Apólice '{numero_apolice_input}' não está ativa. Não é possível registrar sinistro.")
        
        print(f"Apólice: {apolice_encontrada.numero}, Cliente CPF: {apolice_encontrada.cliente_cpf}")

        # --- Bloco de coleta de data ---
        data_ocorrido_str = ""
        while not data_ocorrido_str:
            data_ocorrido_str = input("Data do ocorrido (DD/MM/AAAA): ")
            try:
                data_obj = datetime.datetime.strptime(data_ocorrido_str, "%d/%m/%Y")
                data_formatada_para_salvar = data_obj.strftime("%Y-%m-%d")
            except ValueError:
                data_ocorrido_str = ""
                print("Formato aceito é: DD/MM/AAAA.")
        # -------------------------------

        descricao_sinistro = input("Descrição do sinistro: ")
        if not descricao_sinistro:
            raise RegraNegocioViolada("Descrição é obrigatória!")
        
        status_sinistro_input = ""
        while status_sinistro_input not in ["aberto", "fechado"]:
            status_sinistro_input = input("Status do sinistro (aberto/fechado): ").lower()
            if status_sinistro_input not in ["aberto", "fechado"]:
                print("Status inválido. Por favor, digite 'aberto' ou 'fechado'.")

        novo_sinistro = Sinistro(
            cliente_cpf=apolice_encontrada.cliente_cpf,
            numero_apolice=numero_apolice_input,
            descricao=descricao_sinistro,
            data=data_formatada_para_salvar,
            status=status_sinistro_input
        )
        
        dao.inserir_sinistro(novo_sinistro)
        
        # Log de sucesso
        sistema.registrar_log_operacao(
            logging.INFO, 
            f"SINISTRO ABERTO. Apólice: {numero_apolice_input}, Cliente CPF: {apolice_encontrada.cliente_cpf}."
        )
        print(f"\nSinistro registrado com sucesso!")

    except (DadoInexistente, ApoliceInativa, RegraNegocioViolada) as e:
        sistema.registrar_log_operacao(
            logging.WARNING, 
            f"TENTATIVA DE REGISTRO DE SINISTRO FALHA. Apólice: {numero_apolice_input}. Motivo: {e}"
        )
        print(f"\nERRO: {e}")
    except Exception as e:
        sistema.registrar_log_operacao(logging.ERROR, f"ERRO INESPERADO no registro de sinistro: {e}")
        print(f"\nOcorreu um erro inesperado: {e}")
        
    time.sleep(3)


def sinistros_por_cliente(sistema):
    os.system("cls")
    print("|---------------------=<@>=---------------------|")
    print("        Consulta de Sinistros por Cliente       \n")
    
    try:
        clientes_disponiveis = dao.buscar_todos_clientes()
        if not clientes_disponiveis:
            raise DadoInexistente("Nenhum cliente cadastrado para consulta.")

        cpf_input_consulta = input("Digite o CPF do cliente para consulta: ")
        
        cliente_consultado = dao.buscar_cliente_por_cpf(cpf_input_consulta)
        if not cliente_consultado:
            raise DadoInexistente(f"Cliente com CPF '{cpf_input_consulta}' não encontrado.")

        os.system('cls')
        print(f"\n|---------------------=<@>=---------------------|\n Sinistros para o Cliente: {cliente_consultado.nome}\n                          (CPF: {cpf_input_consulta})\n")
        
        lista_sinistros_do_cliente = [s for s in dao.buscar_todos_sinistros() if s.cliente_cpf == cpf_input_consulta]
        
        if not lista_sinistros_do_cliente:
            print("Nenhum sinistro encontrado para este cliente.")
        else:
            print("  -----------------------------------------------")
            for s_cliente in lista_sinistros_do_cliente:
                print(f"  ID Sinistro: {s_cliente.id}")
                print(f"  Apólice: {s_cliente.numero_apolice}")
                print(f"  Data do Ocorrido: {s_cliente.data}")
                print(f"  Descrição: {s_cliente.descricao}")
                print(f"  Status: {s_cliente.status}")
                print("  -----------------------------------------------")
                
    except DadoInexistente as e:
        print(f"\nERRO: {e}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
            
    input("\nPressione Enter para retornar ao menu...")


def atualizar_status_sinistro(sistema):
    os.system("cls")
    print("|---------------------=<@>=---------------------|")
    print("            Atualizar Status de Sinistro            \n")
    
    sinistro_id = None
    numero_apolice = None
    try:
        numero_apolice = input("Número da apólice do sinistro: ")
        
        sinistros_encontrados = [s for s in dao.buscar_todos_sinistros() if s.numero_apolice == numero_apolice]
        
        if not sinistros_encontrados:
            raise DadoInexistente("Nenhum sinistro encontrado para esta apólice.")
        
        print("\nSinistros encontrados:")
        for i, s in enumerate(sinistros_encontrados, 1):
            print(f"{i}. ID: {s.id}, Data: {s.data}, Descrição: {s.descricao}, Status: {s.status}")
        
        # --- CORREÇÃO: Inicializa 'escolha' e valida no bloco principal ---
        escolha = None
        escolha_str = input("Escolha o NÚMERO do sinistro na lista: ")
        
        if not escolha_str.isdigit():
             raise RegraNegocioViolada("Escolha inválida. Por favor, digite o número da lista.")

        escolha = int(escolha_str) - 1
        if not (0 <= escolha < len(sinistros_encontrados)):
            raise DadoInexistente("Escolha de sinistro inválida.")
        # ------------------------------------------------------------------

        sinistro_selecionado = sinistros_encontrados[escolha]
        sinistro_id = sinistro_selecionado.id 
        
        novo_status = input("Novo status (aberto/fechado): ").lower()
        
        if novo_status == 'fechado':
            sistema.registrar_log_operacao(
                logging.INFO, 
                f"SINISTRO FECHADO/RESOLVIDO. ID: {sinistro_id}, Apólice: {numero_apolice}."
            )
        
        sinistro_selecionado.atualizar_status(novo_status) 
        print("\nStatus atualizado com sucesso!")

    except (DadoInexistente, RegraNegocioViolada) as e:
        sistema.registrar_log_operacao(
            logging.WARNING, 
            f"TENTATIVA DE ATUALIZAÇÃO DE STATUS FALHA. Sinistro ID: {sinistro_id}. Motivo: {e}"
        )
        print(f"\nERRO: {e}")
    except Exception as e:
        sistema.registrar_log_operacao(logging.ERROR, f"ERRO INESPERADO na atualização de sinistro: {e}")
        print(f"\nOcorreu um erro inesperado: {e}")
        
    time.sleep(3)