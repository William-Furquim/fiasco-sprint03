# persistencia.py - VERSÃO FINAL COM EXPORTAÇÃO CSV
import json
import os
import csv
from datetime import datetime

# Cria a pasta 'exports' se ela não existir
EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

# --- Funções de Persistência JSON (Mantidas para a estrutura inicial) ---
def salvar_json(nome, dados):
    """Salva dados em um arquivo JSON."""
    with open(f"{nome}.json", "w", encoding="utf-8") as f:
        # Usa default=lambda o: o.__dict__ para serializar objetos para dicionários
        json.dump(dados, f, indent=4, default=lambda o: o.__dict__)

def carregar_json(nome):
    """Carrega dados de um arquivo JSON."""
    if not os.path.exists(f"{nome}.json"):
        return []
    with open(f"{nome}.json", "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(clientes, seguros, apolices, sinistros):
    """Função central para salvar todos os dados (AGORA PRINCIPALMENTE VIA DAO/SQLITE)."""
    # Esta função pode ser mantida ou removida, dependendo se você quer persistir via JSON
    # ou apenas usar o SQLite. Deixaremos aqui para compatibilidade com o main.py
    # anterior, mas a lógica agora é focada no banco.
    print("Salvamento de dados via JSON foi substituído pelo SQLite.")


def carregar_dados():
    """Função central para carregar dados (AGORA PRINCIPALMENTE VIA DAO/SQLITE)."""
    # Esta função deve ser ignorada se você estiver usando apenas o DAO/SQLite
    return [], [], [], [] 

# --- NOVA FUNÇÃO DE EXPORTAÇÃO CSV ---
def exportar_para_csv(nome_relatorio, dados_lista):
    """
    Exporta uma lista de dicionários para um arquivo CSV na pasta 'exports'.
    A lista deve ser formatada como [{chave: valor}, {chave: valor}].
    """
    if not dados_lista:
        print("Erro: A lista de dados para exportação está vazia.")
        return

    # Garante que as chaves sejam usadas como cabeçalho
    fieldnames = list(dados_lista[0].keys()) 
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f"{nome_relatorio}_{timestamp}.csv"
    caminho_completo = os.path.join(EXPORT_DIR, nome_arquivo)

    try:
        with open(caminho_completo, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

            writer.writeheader()
            writer.writerows(dados_lista)
        
        print(f"\nExportação realizada com sucesso! Arquivo salvo em: {caminho_completo}")

    except Exception as e:
        print(f"\nErro ao exportar para CSV: {e}")