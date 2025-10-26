# dao.py - VERSÃO CORRIGIDA E FINAL

import mysql.connector
from pymongo import MongoClient
import os
import sys
import logging
from logs import log_operacao

mongo_client = MongoClient("mongodb+srv://dmg_db_user:pythonchallenge@dmgcluster.kauhex3.mongodb.net/")
mongo_db = mongo_client["extra_data_logs"]

# Garante que os outros módulos (cliente, seguro, etc.) sejam encontrados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importamos os módulos (arquivos) para uso interno, quebrando a circularidade
import cliente
import apolice
import seguro
import sinistro

# --- FUNÇÕES AUXILIARES (DEVE SER DEFINIDA PRIMEIRO) ---

def get_mysql_connection():
    return mysql.connector.connect(
        host="relacional-core-db.chug4e4ic593.us-east-1.rds.amazonaws.com",
        user="admin",
        password="pythonchallenge",
        database="relacional_core_db"
    )

def _row_to_dict(cursor, row):
    """Converte uma tupla (linha do DB) em um dicionário."""
    col_names = [description[0] for description in cursor.description]
    return dict(zip(col_names, row))

# --- FUNÇÃO DE CRIAÇÃO (CHAMADAS AGORA VÊEM get_db_connection DEFINIDO) ---

def criar_tabelas():
    """Cria todas as tabelas no banco de dados, se não existirem."""
    cfg = {
        'host': 'relacional-core-db.chug4e4ic593.us-east-1.rds.amazonaws.com',
        'user': 'admin',
        'password': 'pythonchallenge'
    }
    tmp_conn = mysql.connector.connect(**cfg)
    tmp_cursor = tmp_conn.cursor()
    tmp_cursor.execute("CREATE DATABASE IF NOT EXISTS seguros_sistema DEFAULT CHARACTER SET 'utf8mb4'")
    tmp_cursor.close()
    tmp_conn.close()
    
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                cpf VARCHAR(20) PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                data_nasc VARCHAR(50),
                endereco TEXT,
                telefone VARCHAR(50),
                email VARCHAR(255)
            ) ENGINE=InnoDB;
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seguros (
                id VARCHAR(100) PRIMARY KEY,
                tipo VARCHAR(100) NOT NULL,
                valor DECIMAL(12,2) NOT NULL,
                modelo VARCHAR(100),
                ano VARCHAR(10),
                placa VARCHAR(20),
                endereco_imovel TEXT,
                beneficiarios TEXT
            ) ENGINE=InnoDB;
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apolices (
                numero VARCHAR(100) PRIMARY KEY,
                cliente_cpf VARCHAR(20) NOT NULL,
                seguro_id VARCHAR(100) NOT NULL,
                valor_mensal DECIMAL(12,2) NOT NULL,
                ativa TINYINT(1) NOT NULL,
                FOREIGN KEY (cliente_cpf) REFERENCES clientes(cpf),
                FOREIGN KEY (seguro_id) REFERENCES seguros(id)
            ) ENGINE=InnoDB;
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sinistros (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_cpf VARCHAR(20) NOT NULL,
                numero_apolice VARCHAR(100) NOT NULL,
                descricao TEXT,
                data VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                FOREIGN KEY (cliente_cpf) REFERENCES clientes(cpf),
                FOREIGN KEY (numero_apolice) REFERENCES apolices(numero)
            ) ENGINE=InnoDB;
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                username VARCHAR(100) PRIMARY KEY,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL
            ) ENGINE=InnoDB;
        """)

        # Inserir usuários padrão (ignorar duplicados)
        try:
            cursor.execute("INSERT INTO usuarios (username, password, role) VALUES ('admin','admin123','admin')")
            cursor.execute("INSERT INTO usuarios (username, password, role) VALUES ('user','user123','user')")
        except mysql.connector.IntegrityError:
            pass

        conn.commit()
    finally:
        cursor.close()
        conn.close()

# --- DAO de Clientes ---

def inserir_cliente(cliente_obj, usuario_log="SISTEMA"):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        data = cliente_obj.to_dict()
        cursor.execute("""
        INSERT INTO clientes (cpf, nome, data_nasc, endereco, telefone, email) 
        VALUES (%(cpf)s, %(nome)s, %(data_nasc)s, %(endereco)s, %(telefone)s, %(email)s)
    """, data)
        conn.commit()
        log_operacao(logging.INFO, 
                     f"Cliente inserido com sucesso: {data['cpf']}", 
                     usuario_log)

    except mysql.connector.IntegrityError:
        log_operacao(logging.WARNING, 
                     f"Falha ao inserir cliente (CPF duplicado): {data['cpf']}", 
                     usuario_log)
        raise ValueError("Erro: Cliente com este CPF já existe.")

    finally:
        conn.close()

def atualizar_cliente(cliente_obj, usuario_log="SISTEMA"):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    data = cliente_obj.to_dict()

    try:
        cursor.execute("""
            UPDATE clientes
            SET telefone = %(telefone)s, email = %(email)s, endereco = %(endereco)s, data_nasc = %(data_nasc)s, nome = %(nome)s
            WHERE cpf = %(cpf)s
        """, data)
        conn.commit()

        if cursor.rowcount > 0:
            log_operacao(logging.INFO,
                         f"Cliente atualizado: {data['cpf']}",
                         usuario_log)
        else:
            log_operacao(logging.WARNING,
                         f"Tentativa atualização cliente não encontrada: {data['cpf']}",
                         usuario_log)

    except mysql.connector.Error as e:
        log_operacao(logging.ERROR,
                     f"Erro ao atualizar cliente {data.get('cpf')}: {e}",
                     usuario_log)
        raise

    finally:
        cursor.close()
        conn.close()


def buscar_cliente_por_cpf(cpf: str):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM clientes WHERE cpf = %(cpf)s", {'cpf': cpf})
        row = cursor.fetchone()
        if row:
            return cliente.Cliente(**row)
        return None
    finally:
        cursor.close()
        conn.close()


def buscar_todos_clientes():
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM clientes")
        rows = cursor.fetchall()
        return [cliente.Cliente(**r) for r in rows]
    finally:
        cursor.close()
        conn.close()

# --- DAO de Seguros ---

def inserir_seguro(seguro_obj, usuario_log="SISTEMA"):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    data = seguro_obj.to_dict()

    # garante chaves opcionais
    for k in ('modelo','ano','placa','endereco_imovel','beneficiarios'):
        data.setdefault(k, None)

    try:
        cursor.execute("""
            INSERT INTO seguros (id, tipo, valor, modelo, ano, placa, endereco_imovel, beneficiarios)
            VALUES (%(id)s, %(tipo)s, %(valor)s, %(modelo)s, %(ano)s, %(placa)s, %(endereco_imovel)s, %(beneficiarios)s)
        """, data)
        conn.commit()
        log_operacao(logging.INFO, f"Seguro inserido: {data['id']}", usuario_log)
    except mysql.connector.IntegrityError:
        log_operacao(logging.WARNING, f"Seguro já existe: {data['id']}", usuario_log)
        raise ValueError("Erro: Seguro já existe.")
    finally:
        cursor.close()
        conn.close()


def buscar_todos_seguros():
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM seguros")
        rows = cursor.fetchall()
        return [seguro.Seguro.from_dict(r) for r in rows]
    finally:
        cursor.close()
        conn.close()

def buscar_seguro_por_id(seguro_id):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM seguros WHERE id = %(id)s", {'id': seguro_id})
        row = cursor.fetchone()
        return seguro.Seguro.from_dict(row) if row else None
    finally:
        cursor.close()
        conn.close()

# --- DAO de Apólices ---

def inserir_apolice(apolice_obj, usuario_log="SISTEMA"):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    data = apolice_obj.to_dict()
    data['ativa'] = 1 if data.get('ativa') else 0

    try:
        cursor.execute("""
            INSERT INTO apolices (numero, cliente_cpf, seguro_id, valor_mensal, ativa)
            VALUES (%(numero)s, %(cliente_cpf)s, %(seguro_id)s, %(valor_mensal)s, %(ativa)s)
        """, data)
        conn.commit()
        log_operacao(logging.INFO, f"Apolice inserida: {data['numero']}", usuario_log)
    except mysql.connector.IntegrityError as e:
        log_operacao(logging.WARNING, f"Erro ao inserir apólice {data.get('numero')}: {e}", usuario_log)
        raise ValueError("Erro: apólice inválida ou duplicada.")
    finally:
        cursor.close()
        conn.close()

def atualizar_status_apolice(numero_apolice: str, status_ativo: bool, usuario_log="SISTEMA"):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    ativa_int = 1 if status_ativo else 0
    try:
        cursor.execute("UPDATE apolices SET ativa = %(ativa)s WHERE numero = %(numero)s",
                       {'ativa': ativa_int, 'numero': numero_apolice})
        conn.commit()
        sucesso = cursor.rowcount > 0
        log_operacao(logging.INFO,
                     f"Atualizar status apólice {numero_apolice} -> {ativa_int}",
                     usuario_log)
        return sucesso
    except mysql.connector.Error as e:
        log_operacao(logging.ERROR, f"Erro atualizar status apólice {numero_apolice}: {e}", usuario_log)
        raise
    finally:
        cursor.close()
        conn.close()

def buscar_apolice_por_numero(numero: str):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM apolices WHERE numero = %(numero)s", {'numero': numero})
        row = cursor.fetchone()
        if row:
            row['ativa'] = bool(row['ativa'])
            return apolice.Apolice(**row)
        return None
    finally:
        cursor.close()
        conn.close()

def buscar_todas_apolices():
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM apolices")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            r['ativa'] = bool(r['ativa'])
            result.append(apolice.Apolice(**r))
        return result
    finally:
        cursor.close()
        conn.close()

# --- DAO de Sinistros ---

def inserir_sinistro(sinistro_obj, usuario_log="SISTEMA"):
    # Parte 1: MySQL (registro relacional)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    data = sinistro_obj.to_dict()
    data.pop('id', None)

    try:
        cursor.execute("""
            INSERT INTO sinistros (cliente_cpf, numero_apolice, descricao, data, status)
            VALUES (%(cliente_cpf)s, %(numero_apolice)s, %(descricao)s, %(data)s, %(status)s)
        """, data)
        conn.commit()
        # Se MySQL criou id autoincrement, pegar lastrowid
        try:
            sinistro_id_sql = cursor.lastrowid
        except:
            sinistro_id_sql = None

        log_operacao(logging.INFO, f"Sinistro inserido (SQL): apólice {data.get('numero_apolice')}", usuario_log)

    except mysql.connector.Error as e:
        log_operacao(logging.ERROR, f"Erro inserir sinistro (SQL): {e}", usuario_log)
        conn.rollback()
        cursor.close()
        conn.close()
        raise

    finally:
        cursor.close()
        conn.close()

    # Parte 2: MongoDB — detalhes, anexos, histórico textual
    try:
        mongo_doc = {
            "sinistro_ref_sql_id": sinistro_id_sql,
            "cliente_cpf": data.get('cliente_cpf'),
            "numero_apolice": data.get('numero_apolice'),
            "descricao_completa": getattr(sinistro_obj, 'descricao', data.get('descricao')),
            "data": data.get('data'),
            "status": data.get('status'),
            # exemplos de campos opcionais: observacoes, anexos, metadata
            "observacoes": getattr(sinistro_obj, 'observacoes', None),
            "anexos": getattr(sinistro_obj, 'anexos', None),
            "criado_por": usuario_log
        }
        mongo_db.sinistros_detalhes.insert_one(mongo_doc)
        log_operacao(logging.INFO, f"Sinistro inserido (MongoDB): apólice {data.get('numero_apolice')}", usuario_log)
    except Exception as e:
        # MongoDB falhar não invalida o registro SQL, apenas logamos o erro para auditoria
        log_operacao(logging.ERROR, f"Erro inserir sinistro (MongoDB): {e}", usuario_log)


def buscar_todos_sinistros(com_detalhes=False):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM sinistros")
        rows = cursor.fetchall()
        sinistros_list = []
        for r in rows:
            s_obj = sinistro.Sinistro(**r)
            if com_detalhes:
                detalhe = mongo_db.sinistros_detalhes.find_one({"numero_apolice": r.get('numero_apolice')})
                if detalhe:
                    # anexar atributos dinâmicos no objeto, se desejar
                    s_obj.observacoes = detalhe.get('observacoes')
                    s_obj.anexos = detalhe.get('anexos')
            sinistros_list.append(s_obj)
        return sinistros_list
    finally:
        cursor.close()
        conn.close()


def atualizar_status_sinistro(sinistro_id: int, novo_status: str, usuario_log="SISTEMA"):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE sinistros SET status = %(status)s WHERE id = %(id)s",
                       {'status': novo_status, 'id': sinistro_id})
        conn.commit()
        sucesso = cursor.rowcount > 0
        log_operacao(logging.INFO, f"Status sinistro {sinistro_id} -> {novo_status}", usuario_log)

        # atualizar também no Mongo se houver documento referenciado
        try:
            mongo_db.sinistros_detalhes.update_many(
                {"sinistro_ref_sql_id": sinistro_id},
                {"$set": {"status": novo_status}}
            )
        except Exception as e:
            log_operacao(logging.WARNING, f"Não foi possível atualizar detalhe Mongo do sinistro {sinistro_id}: {e}", usuario_log)

        return sucesso
    finally:
        cursor.close()
        conn.close()


# --- DAO de Usuários ---

def buscar_usuario_por_credenciais(username, password, usuario_log="SISTEMA"):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT username, role FROM usuarios WHERE username = %(username)s AND password = %(password)s",
                       {'username': username, 'password': password})
        row = cursor.fetchone()
        if row:
            log_operacao(logging.INFO, f"Login bem-sucedido: {username}", usuario_log)
            return {'username': row['username'], 'role': row['role']}
        log_operacao(logging.WARNING, f"Falha de login: {username}", usuario_log)
        return None
    finally:
        cursor.close()
        conn.close()

# --- DAO de Relatórios ---

def calcular_receita_mensal():
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(valor_mensal) FROM apolices WHERE ativa = 1")
        total = cursor.fetchone()[0]
        return float(total) if total is not None else 0.0
    finally:
        cursor.close()
        conn.close()

def ranking_clientes_por_valor_segurado():
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.nome, SUM(s.valor) as total_segurado
            FROM clientes c
            JOIN apolices a ON c.cpf = a.cliente_cpf
            JOIN seguros s ON a.seguro_id = s.id
            WHERE a.ativa = 1
            GROUP BY c.nome
            ORDER BY total_segurado DESC
        """)
        rows = cursor.fetchall()
        ranking = []
        for row in rows:
            ranking.append({'Cliente': row[0], 'Total Segurado (R$)': f"{row[1]:.2f}"})
        return ranking
    finally:
        cursor.close()
        conn.close()

def sinistros_por_status_e_periodo(data_inicio=None, data_fim=None):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT status, COUNT(id) FROM sinistros"
        conds = []
        params = {}
        if data_inicio:
            conds.append("data >= %(data_inicio)s")
            params['data_inicio'] = data_inicio
        if data_fim:
            conds.append("data <= %(data_fim)s")
            params['data_fim'] = data_fim
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " GROUP BY status"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return dict(rows)
    finally:
        cursor.close()
        conn.close()

# Inicialização.
try:
    criar_tabelas()  # agora esta função cria o banco e as tabelas no MySQL
    print("Banco de dados MySQL inicializado e tabelas criadas (se não existiam).")
except Exception as e:
    print(f"Erro ao inicializar banco de dados MySQL: {e}")
