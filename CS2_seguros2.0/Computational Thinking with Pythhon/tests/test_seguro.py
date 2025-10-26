import pytest
from dao import inserir_seguro, buscar_seguro_por_id, get_mysql_connection
from seguro import Seguro

def setup_module(module):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM seguros")
    conn.commit()
    cursor.close()
    conn.close()

def test_inserir_e_buscar_seguro():
    seguro = Seguro(
        id='S001',
        tipo='Automóvel',
        valor=50000.0,
        modelo='Fiat Uno',
        ano='2020',
        placa='ABC-1234'
    )

    inserir_seguro(seguro, usuario_log='TESTE')

    seguro_db = buscar_seguro_por_id('S001')

    assert seguro_db is not None
    assert seguro_db.id == 'S001'
    assert seguro_db.tipo == 'Automóvel'
    assert float(seguro_db.valor) == 50000.0
