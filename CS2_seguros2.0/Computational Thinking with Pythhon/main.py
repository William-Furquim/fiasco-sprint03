#Matheus Cardoso - RM 564898
#Caique Sousa - RM 563621
#Paulo Gabriel - RM 566446
#Davi Gravina - RM 565619
#William Stahl - RM 562800

import os
import time
from persistencia import exportar_para_csv # Importa a exportação
from cliente import cadastrar_cliente, editar_cliente
from seguro import cadastrar_seguro
from apolice import emitir_apolice, listar_apolices_ativas, cancelar_apolice
from sinistro import registrar_sinistro, sinistros_por_cliente, atualizar_status_sinistro
from estado import sistema 
from excecoes import AutenticacaoInvalida 
import dao # Certifique-se que o DAO está importado se a função total_premios foi simplificada

def total_premios():
    os.system("cls")
    
    try:
        # Usa o DAO para calcular o total de prêmios
        total = dao.calcular_receita_mensal()
        
        print("|---------------------=<@>=---------------------|")
        print(f"| Total mensal arrecadado com prêmios: R$ {total:.2f} |")
        print("|---------------------=<@>=---------------------|\n")
        
    except Exception as e:
        print(f"\nERRO ao calcular total de prêmios: {e}")
        
    time.sleep(4)

def menu():
    os.system("cls")
    while True:
        if not sistema.usuario_logado:
            try:
                sistema.login()
            except AutenticacaoInvalida as e:
                print(f"ERRO DE LOGIN: {e}")
                time.sleep(2)
            continue

        linha = "|--------------=<@>=--------------|"
        print(linha)
        
        opcoes = [
            "1-Cadastrar Cliente",
            "2-Cadastrar Seguro",
            "3-Emitir Apólice",
            "4-Listar Apólices Ativas",
            "5-Registrar Sinistro",
            "6-Ver Sinistros por Cliente",
            "7-Total Prêmios Mensais", # Esta opção agora usa total_premios (que usa DAO)
            "8-Editar Cliente",
            "9-Cancelar Apólice",
            "10-Atualizar Status de Sinistro",
            "11-Relatórios Avançados",
            "12-Sair" 
        ]
        
        opcoes_admin = ["1-Cadastrar Cliente", "2-Cadastrar Seguro", "3-Emitir Apólice", 
                        "5-Registrar Sinistro", "8-Editar Cliente", "9-Cancelar Apólice", 
                        "10-Atualizar Status de Sinistro"]
                        
        if not sistema.eh_admin:
            # Filtra as opções restritas para usuários comuns
            opcoes = [op for op in opcoes if op not in opcoes_admin]
        
        print(f"| Usuário: {sistema.usuario_logado} {'(Admin)' if sistema.eh_admin else ''} |\n|")
        for opcao in opcoes:
            print(f"| {opcao} {' ' * (25 - len(opcao))} |")
        print(f"| {linha}\n")
        
        escolha = input("Escolha uma opção: ")
        
        if escolha == "1" and sistema.eh_admin:
            cadastrar_cliente(sistema)
        elif escolha == "2" and sistema.eh_admin:
            cadastrar_seguro(sistema)
        elif escolha == "3" and sistema.eh_admin:
            emitir_apolice(sistema)
        elif escolha == "4":
            listar_apolices_ativas(sistema)
        elif escolha == "5" and sistema.eh_admin:
            registrar_sinistro(sistema)
        elif escolha == "6":
            sinistros_por_cliente(sistema)
        elif escolha == "7":
            total_premios()
        elif escolha == "8" and sistema.eh_admin:
            editar_cliente(sistema)
        elif escolha == "9" and sistema.eh_admin:
            cancelar_apolice(sistema)
        elif escolha == "10" and sistema.eh_admin:
            atualizar_status_sinistro(sistema)
        elif escolha == "11":
            submenu_relatorios()
        elif escolha == "12":
            break
        else:
            print("Opção inválida ou permissão insuficiente.")
            time.sleep(2)

def submenu_relatorios():
    os.system("cls")
    while True:
        print("|---------------------=<@>=---------------------|")
        print("|                Relatórios Avançados                |")
        print("| 1-Receita Mensal Prevista (Prêmios)               |")
        print("| 2-Ranking Clientes por Valor Segurado             |")
        print("| 3-Sinistros por Status e Período (Filtro)         |")
        print("| 4-Apólices por Tipo de Seguro                     |") 
        print("| 5-Sinistros Abertos/Fechados (Geral)              |") 
        print("| 6-Ranking de Clientes por Apólices (Quantidade)   |")
        print("| 7-Voltar                                          |")
        print("|---------------------=<@>=---------------------|\n")
        escolha = input("Escolha uma opção: ")
        
        if escolha == "1":
            sistema.relatorio_receita_mensal_prevista()
        elif escolha == "2":
            sistema.relatorio_valor_segurado_por_cliente()
        elif escolha == "3":
            sistema.relatorio_sinistros_por_periodo()
        elif escolha == "4":
            sistema.relatorio_apolices_por_tipo()
        elif escolha == "5":
            sistema.relatorio_sinistros_status()
        elif escolha == "6":
            sistema.relatorio_ranking_clientes()
        elif escolha == "7":
            break
        else:
            print("Opção inválida.")
            time.sleep(2)

if __name__ == "__main__":
    menu()