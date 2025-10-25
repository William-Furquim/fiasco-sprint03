import pytest
from dao import inserir_sinistro, buscar_todos_sinistros, get_mysql_connection, mongo_db
from sinistro import Sinistro

def setup_module(module):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sinistros")
    conn.commit()
    cursor.close()
    conn.close()

    mongo_db.sinistros_detalhes.delete_many({})

def test_inserir_sinistro_sql_mongo():
    sinistro = Sinistro(
        cliente_cpf="11122233344",
        numero_apolice="A001",
        descricao="Batida traseira em veículo",
        data="21/10/2024",
        status="ABERTO"
    )

    inserir_sinistro(sinistro, usuario_log="TESTE")

    sinistros = buscar_todos_sinistros()
    assert len(sinistros) > 0

    mongo_doc = mongo_db.sinistros_detalhes.find_one({"numero_apolice": "A001"})
    assert mongo_doc is not None
    assert mongo_doc["status"] == "ABERTO"
