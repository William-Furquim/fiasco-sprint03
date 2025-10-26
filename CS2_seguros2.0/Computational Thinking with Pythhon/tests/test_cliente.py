import pytest
from dao import inserir_cliente, buscar_cliente_por_cpf, get_mysql_connection
from cliente import Cliente

def setup_module(module):
    """Limpa a tabela de clientes antes de rodar os testes."""
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes")
    conn.commit()
    cursor.close()
    conn.close()

def test_inserir_e_buscar_cliente():
    cliente = Cliente(
        cpf='11122233344',
        nome='Cliente Teste',
        data_nasc='01/01/2000',
        endereco='Rua A, 123',
        telefone='11999999999',
        email='teste@example.com'
    )

    inserir_cliente(cliente, usuario_log='TESTE')

    cliente_db = buscar_cliente_por_cpf('11122233344')

    assert cliente_db is not None
    assert cliente_db.cpf == '11122233344'
    assert cliente_db.nome == 'Cliente Teste'
