# excecoes.py

class ErroSistemaSeguros(Exception):
    """Superclasse para todas as exceções de negócio do sistema."""
    pass

class AutenticacaoInvalida(ErroSistemaSeguros):
    """Exceção levantada quando o login falha."""
    def __init__(self, message="Usuário ou senha inválidos."):
        super().__init__(message)

class DadoJaExiste(ErroSistemaSeguros):
    """Exceção levantada ao tentar cadastrar um dado que já existe (Ex: CPF duplicado)."""
    pass

class DadoInexistente(ErroSistemaSeguros):
    """Exceção levantada ao tentar buscar ou operar um registro que não existe."""
    pass

class ApoliceInativa(DadoInexistente):
    """Exceção levantada ao tentar operar uma apólice cancelada ou inativa."""
    pass

class OperacaoNaoPermitida(ErroSistemaSeguros):
    """Exceção levantada quando um usuário tenta realizar uma ação para a qual não tem permissão (ex: Comum tentando cadastrar)."""
    pass

class RegraNegocioViolada(ErroSistemaSeguros):
    """Exceção genérica para outras violações de regras (ex: data incoerente, campo vazio)."""
    pass