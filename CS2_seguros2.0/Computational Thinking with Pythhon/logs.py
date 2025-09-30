# logs.py - VERSÃO CORRIGIDA E FINAL
import logging
import os
from datetime import datetime

LOG_FILE = f"auditoria_{datetime.now().strftime('%Y%m%d')}.log"
LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Garante que a pasta de logs exista
os.makedirs(LOG_DIR, exist_ok=True)

def configurar_logging():
    """Configura o sistema de logging (console e arquivo)."""
    
    logger = logging.getLogger()
    
    # Adiciona o filtro customizado antes de qualquer handler
    class UserFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, 'user'):
                record.user = 'NAO_LOGADO/SISTEMA'
            return True
            
    logger.addFilter(UserFilter())
    
    # 1. Configuração do Formato Padrão (Console)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - (USUARIO: %(user)s) - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 2. Handler para o arquivo de log (AUDITORIA)
    file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | USUARIO: %(user)s | OPERACAO: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Adiciona o FileHandler apenas se não existir (evita duplicidade)
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        logger.addHandler(file_handler)
    
    # Nível global
    logger.setLevel(logging.INFO)

# Obter o logger principal
sistema_logger = logging.getLogger()

# Função auxiliar para registrar log (simplifica o uso)
def log_operacao(level, message, user_log):
    """Registra uma mensagem de log com o usuário logado."""
    sistema_logger.log(level, message, extra={'user': user_log})

# Inicializa a configuração
configurar_logging()

# Log de inicialização (agora gravado após a configuração completa)
log_operacao(logging.INFO, "Sistema de Seguros inicializado.", 'SISTEMA')