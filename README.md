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

### 2\. Arquitetura dos Dados

O sistema utiliza uma arquitetura de persistência de dados híbrida, dividida em três camadas principais:

Banco de dados relacional (MySQL):
Essa camada é responsável por armazenar todas as informações estruturadas e que possuem relações entre si. Aqui ficam armazenados os dados de Clientes, Seguros, Apólices e Sinistros. São dados organizados em tabelas, com chaves primárias e estrangeiras, permitindo integridade e consistência.

Banco de dados não relacional (MongoDB):
Essa camada armazena dados que não são facilmente estruturados em tabelas ou que podem variar de formato, como observações extensas de sinistros, anexos, relatórios, informações adicionais e logs de auditoria mais detalhados. Cada registro é salvo no formato de documento (JSON), oferecendo flexibilidade.

Auditoria em arquivo (pasta /logs/):
Além dos bancos de dados, o sistema mantém um arquivo de auditoria diário no formato .log. Esses arquivos são armazenados dentro da pasta logs/ e seguem o padrão de nome auditoria_YYYYMMDD.log, registrando todas as ações importantes feitas no sistema, como operações de cadastro, alterações e erros.

#### Como Executar o Sistema
1. Configure o MySQL

Crie o banco de dados manualmente ou deixe o sistema fazer isso na primeira execução.

CREATE DATABASE seguros_sistema;


Ou apenas rode o programa, pois o dao.py executa automaticamente:

criar_tabelas()  # Cria tabelas se não existirem

2. Configure o MongoDB (opcional se estiver local)

MongoDB será criado automaticamente quando os primeiros logs forem inseridos:

Database: seguros_sistema_mongo

Colections usadas:

logs

sinistros_detalhes (observações e dados extras)

3. Execute o sistema:
python main.py

4. Executar migração de dados dos JSONs:
python migracao.py

#### Credenciais Padrão (armazenadas no MySQL)
Perfil	Usuário	Senha	Permissões
Admin	admin	admin123	Total
Usuário	user	user123	Apenas consulta
#### Principais Arquivos do Projeto
Arquivo	Função
dao.py	Camada de dados — agora usa MySQL + MongoDB
migracao.py	Importa JSONs para o MySQL
logs.py	Sistema de auditoria (arquivo .log + MongoDB)
main.py	Menu principal e controle do fluxo
cliente.py, seguro.py, apolice.py, sinistro.py	Classes de modelo
### 3\. Persistência Híbrida — Como funciona?
- MySQL — Dados estruturados (ACID)

O MySQL é o banco de dados responsável por armazenar todas as informações estruturadas do sistema, ou seja, os dados que possuem um formato fixo, relações entre si e precisam garantir integridade e consistência. Ele é utilizado por ser um banco relacional que segue o modelo ACID (Atomicidade, Consistência, Isolamento e Durabilidade), o que torna as operações mais seguras e confiáveis.

Dentro dele ficam armazenados:

Clientes: dados cadastrais como CPF, nome, endereço, e-mail, telefone e data de nascimento.

Seguros: informações sobre os tipos de seguros oferecidos (automóvel, vida, residência, etc.), valores, modelo, ano, placa ou dados do imóvel, dependendo do tipo.

Apólices: registros que fazem a ligação entre o cliente e o seguro contratado, contendo número da apólice, valor mensal e se está ativa ou não.

Sinistros (dados básicos): ocorrências registradas pelo cliente, com CPF, número da apólice, data, status e uma descrição resumida.

Esses dados estruturados permanecem no MySQL para garantir organização, relacionamento entre tabelas (por meio de chaves estrangeiras) e para facilitar consultas, relatórios e cálculos.
- MongoDB — Dados complementares

O MongoDB é utilizado no sistema para armazenar informações complementares, ou seja, dados que não se encaixam bem no formato de tabelas relacionais do MySQL. Esse banco é ideal para guardar conteúdos mais flexíveis, que podem variar muito de tamanho, estrutura e quantidade de informações.
Dentro dele, utilizamos coleções específicas para diferentes tipos de dados:

Coleção logs:
Armazena os registros de auditoria referentes às operações realizadas no sistema. Isso inclui ações como cadastro, consultas, alterações, exclusões, tentativas de login e possíveis erros. Cada log contém informações como data e hora, usuário que executou a ação, tipo da operação e detalhes relevantes.

Coleção sinistros_detalhes:
Essa coleção guarda dados mais completos e desestruturados relacionados a sinistros. São informações que o MySQL não armazena bem, como descrições muito longas, observações adicionais, relatórios, imagens, documentos anexados ou metadados específicos do sinistro.

Coleção perfil_cliente (opcional):
Pode ser usada para armazenar dados mais subjetivos sobre o cliente, como histórico de interações, preferências, nível de engajamento e anotações que não fazem parte do cadastro formal armazenado no MySQL.
