# migracao.py - VERSÃO FINAL CORRIGIDA
import json
import os
import dao

# Importamos os módulos para podermos instanciar os objetos
import cliente
import seguro
import apolice
import sinistro
from datetime import datetime
import time

# --- FUNÇÃO DE CARREGAMENTO (Com a melhoria de debug) ---
def carregar_json(nome):
    """Carrega JSON usando codificações diferentes se necessário, e imprime o status."""
    filename = f"{nome}.json"
    if not os.path.exists(filename):
        print(f"DEBUG: Arquivo {filename} NÃO ENCONTRADO.")
        return []
    
    data = []
    try:
        # Tenta ler com a codificação padrão (utf-8)
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"DEBUG: {filename} falhou com UTF-8. Tentando ISO-8859-1 (Latin-1)...")
        try:
            # Tenta ler com Latin-1 (comum em sistemas Windows mais antigos)
            with open(filename, "r", encoding="iso-8859-1") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"AVISO: Arquivo {filename} está corrompido ou vazio.")
            return []
    except Exception as e:
        print(f"AVISO: Erro de leitura de arquivo inesperado em {filename}: {e}")
        return []

    print(f"DEBUG: {filename} lido com sucesso. Itens encontrados: {len(data)}")
    return data

# --- FUNÇÃO DE MIGRAÇÃO (Lógica simplificada - OPÇÃO 2) ---
def migrar_entidade(entidade_nome, dados_json, entidade_classe, inserir_dao_func):
    """Função genérica para migrar dados de um JSON para o DAO, tratando Seguros de forma especial."""
    print(f"--- Migrando {entidade_nome} ---")
    migrados = 0
    
    if not dados_json:
        print(f"AVISO: {entidade_nome} está vazio. Pulando migração.")
        return

    for i, data in enumerate(dados_json):
        try:
            # LÓGICA CRÍTICA CORRIGIDA: Trata Seguros com from_dict e o resto com **data
            if entidade_nome == "Seguros":
                # Para Seguros, chamamos diretamente o from_dict da classe Seguro, passando o dicionário inteiro
                obj = seguro.Seguro.from_dict(data) 
            else:
                # Para Clientes, Apólices e Sinistros, usamos o construtor padrão com desempacotamento
                obj = entidade_classe(**data)
            
            inserir_dao_func(obj)
            migrados += 1
            
        except TypeError as e:
            # Erro Comum: Chaves erradas/faltando (O JSON não corresponde à classe)
            print(f"ERRO CRÍTICO (ITEM {i+1} - TIPO): Falha ao criar objeto {entidade_nome}. O JSON NÃO CORRESPONDE à classe. Erro: {e}")
            print(f"  -> Dados problemáticos: {data}")
            
        except ValueError as e:
            # Erro Comum: Regra de Negócio/DAO (Ex: CPF duplicado)
            print(f"AVISO (ITEM {i+1} - VALOR): {e} - Dados: {data}")

        except Exception as e:
            # Erros Inesperados
            print(f"ERRO INESPERADO (ITEM {i+1}): {e} - Dados: {data}")
            
    print(f"{entidade_nome} migrados com sucesso: {migrados}")


def executar_migracao():
    """Executa a rotina completa de migração."""
    
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - (USUARIO: SISTEMA) - Sistema de Seguros inicializado.")
    dao.criar_tabelas() # Garante que as tabelas existam
    
    # --- 1. Carregar JSONs ---
    print("\n--- INICIANDO MIGRAÇÃO JSON -> SQLITE ---")
    print("Carregando dados antigos do JSON...")
    
    # NOTA: Passamos a CLASSE, não o MÉTODO, para clientes, apolices e sinistros.
    clientes_json = carregar_json("clientes")
    seguros_json = carregar_json("seguros")
    apolices_json = carregar_json("apolices")
    sinistros_json = carregar_json("sinistros")

    # --- 2. Migração para o DAO ---
    
    # Clientes
    migrar_entidade("Clientes", clientes_json, cliente.Cliente, dao.inserir_cliente)

    # Seguros (Passamos a CLASSE, e a função migrar_entidade chamará o from_dict)
    migrar_entidade("Seguros", seguros_json, seguro.Seguro, dao.inserir_seguro)

    # Apólices
    migrar_entidade("Apólices", apolices_json, apolice.Apolice, dao.inserir_apolice)
    
    # Sinistros
    migrar_entidade("Sinistros", sinistros_json, sinistro.Sinistro, dao.inserir_sinistro)
    
    print("\n--- MIGRAÇÃO CONCLUÍDA! Seu sistema agora usa SQLite. ---")

if __name__ == "__main__":
    executar_migracao()