# Sistema de Gestão de Apólices - Sprint 4: Persistência Híbrida (MySQL + MongoDB)

Este sistema gerencia clientes, seguros, apólices e sinistros.
Na Sprint atual, o projeto foi evoluído para utilizar persistência híbrida em dois bancos de dados:

- MySQL → dados estruturados e relacionais (clientes, seguros, apólices, sinistros)
- MongoDB → dados não estruturados (logs, anexos, observações longas de sinistros, histórico de ações)
- Logs de auditoria automatizados → arquivo .log e MongoDB

## 🧑‍💻 Integrantes do Grupo FIASCO

| Nome | RM |
| :--- | :--- |
| Matheus Cardoso | 564898 |
| Caique Sousa | 563621 |
| Paulo Gabriel | 566446 |
| Davi Gravina | 565619 |
| William Stahl | 562800 |

## 🚀 Requisitos para Execução

  * **Linguagem:** Python 3.8 ou superior.
  * **Bibliotecas:** As bibliotecas padrão do Python (`mysql-connector-python`, `pymongo`, `csv`, `logging`, `os`, etc.) Instale as dependências com: `pip install mysql-connector-python pymongo`

## 💾 Instruções de Instalação e Execução

### 1\. Preparação dos Arquivos

1.  Extraia o conteúdo do projeto em uma única pasta.
2.  Confirme que os arquivos Python (`main.py`, `dao.py`, `migracao.py`, `excecoes.py`, `logs.py`, etc.) e os arquivos JSON de exemplo (`*.json`) estão presentes.

### 2\. Inicialização do Banco de Dados (SQLite)

🗄️ Arquitetura dos Dados
Camada	Banco	O que armazena
Relacional	MySQL	Clientes, Seguros, Apólices, Sinistros (informações principais)
Documentos	MongoDB	Logs, observações extensas, anexos, auditoria detalhada
Auditoria em arquivo	/logs/	Histórico diário de ações: auditoria_YYYYMMDD.log
🚀 Como Executar o Sistema
✅ 1. Configure o MySQL

Crie o banco de dados manualmente ou deixe o sistema fazer isso na primeira execução.

CREATE DATABASE seguros_sistema;


Ou apenas rode o programa, pois o dao.py executa automaticamente:

criar_tabelas()  # Cria tabelas se não existirem

✅ 2. Configure o MongoDB (opcional se estiver local)

MongoDB será criado automaticamente quando os primeiros logs forem inseridos:

Database: seguros_sistema_mongo

Colections usadas:

logs

sinistros_detalhes (observações e dados extras)

✅ 3. Execute o sistema:
python main.py

✅ 4. Executar migração de dados dos JSONs:
python migracao.py

🔐 Credenciais Padrão (armazenadas no MySQL)
Perfil	Usuário	Senha	Permissões
Admin	admin	admin123	Total
Usuário	user	user123	Apenas consulta
📂 Principais Arquivos do Projeto
Arquivo	Função
dao.py	Camada de dados — agora usa MySQL + MongoDB
migracao.py	Importa JSONs para o MySQL
logs.py	Sistema de auditoria (arquivo .log + MongoDB)
main.py	Menu principal e controle do fluxo
cliente.py, seguro.py, apolice.py, sinistro.py	Classes de modelo
📡 Persistência Híbrida — Como funciona?
✅ MySQL — Dados estruturados (ACID)

Clientes (clientes)

Seguros (seguros)

Apólices (apolices)

Sinistros básicos (sinistros)

✅ MongoDB — Dados complementares

Usamos para armazenar informações que não são bem estruturadas em tabelas relacionais:

Coleção Mongo	O que guarda?
logs	Cada operação do sistema (CRUD, login, erro) com timestamp e usuário
sinistros_detalhes	Observações longas, imagens, relatórios extensos
perfil_cliente (opcional)	Preferências, histórico de contato
