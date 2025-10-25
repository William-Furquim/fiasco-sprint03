import os
from logs import log_operacao
from dao import mongo_db

def test_log_em_arquivo():
    from datetime import datetime
    hoje = datetime.now().strftime("%Y%m%d")
    caminho_arquivo = f"logs/auditoria_{hoje}.log"

    log_operacao(20, "Teste de log em arquivo", "TESTE")

    assert os.path.exists(caminho_arquivo), "Arquivo de log não foi criado!"

    with open(caminho_arquivo, "r") as f:
        conteudo = f.read()
        assert "Teste de log em arquivo" in conteudo

def test_log_no_mongodb():
    log_operacao(20, "Teste de log no MongoDB", "TESTE")

    resultado = mongo_db.logs.find_one({"mensagem": {"$regex": "Teste de log no MongoDB"}})
    assert resultado is not None
    assert resultado["usuario"] == "TESTE"
