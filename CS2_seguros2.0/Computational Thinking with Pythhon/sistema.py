# sistema.py - Versão FINAL (Com Correção de Login e Relatórios Avançados)

import os
import time
import dao 
from excecoes import AutenticacaoInvalida 
from logs import log_operacao, logging 
from persistencia import exportar_para_csv # Importa a nova função

class SistemaSeguros:
    def __init__(self):
        # CORREÇÃO: Inicializa como None para que o main.py force o login
        self.usuario_logado = None 
        self.eh_admin = False
        dao.criar_tabelas() 

    def login(self):
        os.system("cls")
        print("|---------------------=<@>=---------------------|")
        print("                  Login no Sistema                  \n")
        usuario = input("Usuário: ")
        senha = input("Senha: ")
        
        user_data = dao.buscar_usuario_por_credenciais(usuario, senha)

        if user_data:
            self.usuario_logado = user_data['username']
            self.eh_admin = user_data['role'] == "admin"
            
            self.registrar_log_operacao(logging.INFO, "Login bem-sucedido.")
            
            print("Login realizado com sucesso!")
        else:
            log_operacao(logging.WARNING, f"Tentativa de login falhou para o usuário: {usuario}.", 'TENTATIVA')
            raise AutenticacaoInvalida("Usuário ou senha inválidos.")
        time.sleep(2)

    def registrar_log_operacao(self, level, mensagem):
        """Função auxiliar para logs de ações do usuário logado."""
        log_operacao(level, mensagem, self.usuario_logado)

    # --- Métodos de acesso ao DAO (Busca de objetos) ---
    def _get_clientes(self):
        return dao.buscar_todos_clientes()
    
    def _get_seguros(self):
        return dao.buscar_todos_seguros()
    
    def _get_apolices(self):
        return dao.buscar_todas_apolices()

    def _get_sinistros(self):
        return dao.buscar_todos_sinistros()
    # -----------------------------------------------------------------

    # --- Implementação dos Relatórios Avançados ---

    def relatorio_receita_mensal_prevista(self):
        os.system("cls")
        print("|---------------------=<@>=---------------------|")
        print("          Receita Mensal Prevista (Prêmios)         \n")
        
        total = dao.calcular_receita_mensal()
        
        print(f"Total de Prêmios Mensais de Apólices Ativas: R$ {total:.2f}")

        input("\nPressione Enter para retornar...")

    def relatorio_valor_segurado_por_cliente(self):
        os.system("cls")
        print("|---------------------=<@>=---------------------|")
        print("        Ranking: Top Clientes por Valor Segurado      \n")
        
        ranking = dao.ranking_clientes_por_valor_segurado() 
        
        if not ranking:
            print("Nenhuma apólice ativa encontrada para calcular o ranking.")
            input("\nPressione Enter para retornar...")
            return
            
        print("RANKING:")
        for i, item in enumerate(ranking, 1):
            print(f"{i}. Cliente: {item['Cliente']} | Valor Segurado: R$ {item['Total Segurado (R$)']}")

        if input("\nDeseja exportar para CSV? (s/n): ").lower() == 's':
            exportar_para_csv("ranking_valor_segurado", ranking)

        input("\nPressione Enter para retornar...")
    
    def relatorio_sinistros_por_periodo(self):
        os.system("cls")
        print("|---------------------=<@>=---------------------|")
        print("        Sinistros por Status e Período        \n")
        
        print("Filtros (deixe vazio para não aplicar):")
        data_inicio = input("Data de Início (AAAA-MM-DD): ")
        data_fim = input("Data de Fim (AAAA-MM-DD): ")
        
        try:
            # Chama a função do DAO
            resultado_dict = dao.sinistros_por_status_e_periodo(data_inicio or None, data_fim or None)
        except Exception as e:
            print(f"\nERRO ao buscar no banco: Verifique o formato da data (AAAA-MM-DD). Erro: {e}")
            input("\nPressione Enter para retornar...")
            return

        print("\nRESULTADO:")
        print("Status Abertos: ", resultado_dict.get('aberto', 0))
        print("Status Fechados: ", resultado_dict.get('fechado', 0))
        print("---------------------------------")
        
        # Formata para exportação CSV (lista de dicionários)
        dados_export = [
            {'Status': 'Aberto', 'Quantidade': resultado_dict.get('aberto', 0)},
            {'Status': 'Fechado', 'Quantidade': resultado_dict.get('fechado', 0)}
        ]
        
        if input("\nDeseja exportar para CSV? (s/n): ").lower() == 's':
            exportar_para_csv("sinistros_status_periodo", dados_export)

        input("\nPressione Enter para retornar...")


    # --- Relatórios Antigos (Mantidos para compatibilidade) ---
    def relatorio_apolices_por_tipo(self):
        os.system("cls")
        print("|---------------------=<@>=---------------------|")
        print("         Apólices Emitidas por Tipo de Seguro         \n")
        tipos = {"Automóvel": 0, "Residencial": 0, "Vida": 0}
        
        apolices = self._get_apolices()
        seguros = self._get_seguros()
        
        for apolice in apolices:
            if apolice.ativa:
                seguro_obj = next((s for s in seguros if s.id == apolice.seguro_id), None)
                if seguro_obj:
                    tipos[seguro_obj.tipo] += 1
        
        dados_export = [{'Tipo': k, 'Quantidade': v} for k, v in tipos.items()]
        
        for tipo, quantidade in tipos.items():
            print(f"Tipo: {tipo}, Quantidade: {quantidade}")

        if input("\nDeseja exportar para CSV? (s/n): ").lower() == 's':
            exportar_para_csv("apolices_por_tipo", dados_export)

        input("Pressione Enter para retornar...")

    def relatorio_sinistros_status(self):
        # Este é o relatório geral de sinistros abertos/fechados (Opção 5 no menu)
        os.system("cls")
        print("|---------------------=<@>=---------------------|")
        print("         Quantidade de Sinistros Abertos/Fechados (Geral)         \n")
        
        sinistros = self._get_sinistros() 
        
        abertos = sum(1 for s in sinistros if s.status == "aberto")
        fechados = sum(1 for s in sinistros if s.status == "fechado")
        
        print(f"Sinistros abertos: {abertos}")
        print(f"Sinistros fechados: {fechados}")
        input("Pressione Enter para retornar...")

    def relatorio_ranking_clientes(self):
        # Este relatório não foi substituído pela nova função DAO para evitar quebra.
        # Ele calcula o ranking por QTD de apólices, não por Valor Segurado.
        os.system("cls")
        print("|---------------------=<@>=---------------------|")
        print("         Ranking de Clientes por Apólices (Quantidade)         \n")
        ranking = {}
        
        clientes = self._get_clientes()
        apolices = self._get_apolices()
        
        for cliente_obj in clientes:
            count = sum(1 for a in apolices if a.cliente_cpf == cliente_obj.cpf and a.ativa)
            ranking[cliente_obj.nome] = count
            
        ranking_ordenado = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
        
        dados_export = [{'Cliente': nome, 'Apólices Ativas': quantidade} for nome, quantidade in ranking_ordenado]
        
        for nome, quantidade in ranking_ordenado:
            print(f"Cliente: {nome}, Apólices: {quantidade}")

        if input("\nDeseja exportar para CSV? (s/n): ").lower() == 's':
            exportar_para_csv("ranking_clientes_quantidade", dados_export)

        input("Pressione Enter para retornar...")