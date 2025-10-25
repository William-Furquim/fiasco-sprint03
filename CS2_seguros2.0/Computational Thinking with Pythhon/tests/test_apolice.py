import pytest
from dao import inserir_apolice, buscar_apolice_por_numero, get_mysql_connection
from apolice import Apolice

def setup_module(module):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM apolices")
    conn.commit()
    cursor.close()
    conn.close()

def test_inserir_e_buscar_apolice():
    apolice = Apolice(
        numero='A001',
        cliente_cpf='11122233344',
        seguro_id='S001',
        valor_mensal=200.0,
        ativa=True
    )

    inserir_apolice(apolice, usuario_log='TESTE')

    apolice_db = buscar_apolice_por_numero('A001')

    assert apolice_db is not None
    assert apolice_db.numero == 'A001'
    assert apolice_db.cliente_cpf == '11122233344'
    assert float(apolice_db.valor_mensal) == 200.0
