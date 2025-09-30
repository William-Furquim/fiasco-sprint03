# dao.py - VERSÃO CORRIGIDA E FINAL

import sqlite3
import os
import sys

# Garante que os outros módulos (cliente, seguro, etc.) sejam encontrados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importamos os módulos (arquivos) para uso interno, quebrando a circularidade
import cliente
import apolice
import seguro
import sinistro 

# Nome do arquivo do banco de dados
DB_NAME = "seguros_sistema.db"

# --- FUNÇÕES AUXILIARES (DEVE SER DEFINIDA PRIMEIRO) ---

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    return sqlite3.connect(DB_NAME)

def _row_to_dict(cursor, row):
    """Converte uma tupla (linha do DB) em um dicionário."""
    col_names = [description[0] for description in cursor.description]
    return dict(zip(col_names, row))

# --- FUNÇÃO DE CRIAÇÃO (CHAMADAS AGORA VÊEM get_db_connection DEFINIDO) ---

def criar_tabelas():
    """Cria todas as tabelas no banco de dados, se não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabela Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            cpf TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            data_nasc TEXT,
            endereco TEXT,
            telefone TEXT,
            email TEXT
        );
    """)

    # Tabela Seguros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seguros (
            id TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            modelo TEXT,
            ano TEXT,
            placa TEXT,
            endereco_imovel TEXT,
            beneficiarios TEXT
        );
    """)

    # Tabela Apolices
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apolices (
            numero TEXT PRIMARY KEY,
            cliente_cpf TEXT NOT NULL,
            seguro_id TEXT NOT NULL,
            valor_mensal REAL NOT NULL,
            ativa INTEGER NOT NULL,
            FOREIGN KEY (cliente_cpf) REFERENCES clientes(cpf),
            FOREIGN KEY (seguro_id) REFERENCES seguros(id)
        );
    """)

    # Tabela Sinistros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sinistros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_cpf TEXT NOT NULL,
            numero_apolice TEXT NOT NULL,
            descricao TEXT,
            data TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (cliente_cpf) REFERENCES clientes(cpf),
            FOREIGN KEY (numero_apolice) REFERENCES apolices(numero)
        );
    """)

    # Tabela Usuarios (para o requisito 6 - Autenticação)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL -- 'admin' ou 'user'
        );
    """)

    # Inserir usuários padrão para login (se não existirem)
    try:
        cursor.execute("INSERT INTO usuarios VALUES ('admin', 'admin123', 'admin')")
        cursor.execute("INSERT INTO usuarios VALUES ('user', 'user123', 'user')")
    except sqlite3.IntegrityError:
        pass 

    conn.commit()
    conn.close()

# --- DAO de Clientes ---

def inserir_cliente(cliente_obj):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data = cliente_obj.to_dict()
        cursor.execute("""
            INSERT INTO clientes VALUES (:cpf, :nome, :data_nasc, :endereco, :telefone, :email)
        """, data)
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Erro: Cliente com este CPF já existe.")
    finally:
        conn.close()

def atualizar_cliente(cliente_obj):
    conn = get_db_connection()
    cursor = conn.cursor()
    data = cliente_obj.to_dict()
    cursor.execute("""
        UPDATE clientes SET telefone = :telefone, email = :email WHERE cpf = :cpf
    """, data)
    conn.commit()
    conn.close()

def buscar_cliente_por_cpf(cpf: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE cpf = ?", (cpf,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = _row_to_dict(cursor, row)
        return cliente.Cliente(**data) 
    return None

def buscar_todos_clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    rows = cursor.fetchall()
    conn.close()
    
    clientes_list = []
    for row in rows:
        data = _row_to_dict(cursor, row)
        clientes_list.append(cliente.Cliente(**data)) 
    return clientes_list

# --- DAO de Seguros ---

def inserir_seguro(seguro_obj):
    conn = get_db_connection()
    cursor = conn.cursor()
    data = seguro_obj.to_dict()
    
    if 'modelo' not in data: data['modelo'] = None
    if 'ano' not in data: data['ano'] = None
    if 'placa' not in data: data['placa'] = None
    if 'endereco_imovel' not in data: data['endereco_imovel'] = None
    if 'beneficiarios' not in data: data['beneficiarios'] = None

    cursor.execute("""
        INSERT INTO seguros VALUES (:id, :tipo, :valor, :modelo, :ano, :placa, :endereco_imovel, :beneficiarios)
    """, data)
    conn.commit()
    conn.close()

def buscar_todos_seguros():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seguros")
    rows = cursor.fetchall()
    conn.close()
    
    seguros_list = []
    for row in rows:
        data = _row_to_dict(cursor, row)
        seguros_list.append(seguro.Seguro.from_dict(data)) 
    return seguros_list

def buscar_seguro_por_id(seguro_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seguros WHERE id = ?", (seguro_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = _row_to_dict(cursor, row)
        return seguro.Seguro.from_dict(data)
    return None

# --- DAO de Apólices ---

def inserir_apolice(apolice_obj):
    conn = get_db_connection()
    cursor = conn.cursor()
    data = apolice_obj.to_dict()
    data['ativa'] = 1 if data['ativa'] else 0
    
    cursor.execute("""
        INSERT INTO apolices VALUES (:numero, :cliente_cpf, :seguro_id, :valor_mensal, :ativa)
    """, data)
    conn.commit()
    conn.close()

def atualizar_status_apolice(numero_apolice: str, status_ativo: bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    ativa_int = 1 if status_ativo else 0
    cursor.execute("UPDATE apolices SET ativa = ? WHERE numero = ?", (ativa_int, numero_apolice))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def buscar_apolice_por_numero(numero: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apolices WHERE numero = ?", (numero,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = _row_to_dict(cursor, row)
        data['ativa'] = bool(data['ativa'])
        return apolice.Apolice(**data) 
    return None

def buscar_todas_apolices():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apolices")
    rows = cursor.fetchall()
    conn.close()
    
    apolices_list = []
    for row in rows:
        data = _row_to_dict(cursor, row)
        data['ativa'] = bool(data['ativa'])
        apolices_list.append(apolice.Apolice(**data)) 
    return apolices_list

# --- DAO de Sinistros ---

def inserir_sinistro(sinistro_obj):
    conn = get_db_connection()
    cursor = conn.cursor()
    data = sinistro_obj.to_dict()
    data.pop('id', None) 
    
    cursor.execute("""
        INSERT INTO sinistros (cliente_cpf, numero_apolice, descricao, data, status)
        VALUES (:cliente_cpf, :numero_apolice, :descricao, :data, :status)
    """, data)
    conn.commit()
    conn.close()

def buscar_todos_sinistros():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sinistros")
    rows = cursor.fetchall()
    conn.close()
    
    sinistros_list = []
    for row in rows:
        data = _row_to_dict(cursor, row)
        sinistros_list.append(sinistro.Sinistro(**data)) 
    return sinistros_list

def atualizar_status_sinistro(sinistro_id: int, novo_status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sinistros SET status = ? WHERE id = ?", (novo_status, sinistro_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

# --- DAO de Usuários ---

def buscar_usuario_por_credenciais(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM usuarios WHERE username = ? AND password = ?", (username, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'username': row[0], 'role': row[1]}
    return None

# --- DAO de Relatórios ---

def calcular_receita_mensal():
    """Calcula a soma dos valores mensais das apólices ativas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor_mensal) FROM apolices WHERE ativa = 1")
    total = cursor.fetchone()[0]
    conn.close()
    return total if total is not None else 0.0

def ranking_clientes_por_valor_segurado():
    """
    Retorna uma lista de dicionários contendo o nome e o total segurado 
    para cada cliente (somando o 'valor' dos seguros ativos).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.nome, 
            SUM(s.valor) as total_segurado
        FROM clientes c
        JOIN apolices a ON c.cpf = a.cliente_cpf
        JOIN seguros s ON a.seguro_id = s.id
        WHERE a.ativa = 1 
        GROUP BY c.nome
        ORDER BY total_segurado DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    ranking = []
    for row in rows:
        ranking.append({
            'Cliente': row[0], 
            'Total Segurado (R$)': f"{row[1]:.2f}"
        })
    return ranking
    
def sinistros_por_status_e_periodo(data_inicio=None, data_fim=None):
    """
    Conta sinistros por status ('aberto' ou 'fechado') e opcionalmente por período.
    Retorna um dicionário com as contagens.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT status, COUNT(id) FROM sinistros"
    conditions = []
    params = []
    
    if data_inicio:
        conditions.append("data >= ?")
        params.append(data_inicio)
        
    if data_fim:
        conditions.append("data <= ?")
        params.append(data_fim)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " GROUP BY status"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    resultado = dict(rows)
    return resultado

# Inicializa o banco de dados (cria o arquivo e as tabelas se não existirem)
if not os.path.exists(DB_NAME):
    criar_tabelas()
    print(f"Banco de dados '{DB_NAME}' inicializado e tabelas criadas.")