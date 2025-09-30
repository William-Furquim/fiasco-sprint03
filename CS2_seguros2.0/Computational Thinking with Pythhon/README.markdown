# Sistema de Gestão de Apólices - Sprint 3: Persistência Robusta e Auditoria

Este é um programa em Python para gerenciar apólices de seguros, feito pelo grupo **FIASCO** para a **Sprint 3** do nosso projeto. O sistema foi migrado para um **banco de dados SQLite** para garantir **persistência robusta**, adicionamos um módulo de **Auditoria (Logs)** para rastrear todas as operações críticas e implementamos **Tratamento de Erros** para uma CLI mais amigável.

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
  * **Bibliotecas:** Apenas as bibliotecas padrão do Python (`sqlite3`, `csv`, `logging`, `os`, etc.). Nenhuma instalação extra é necessária.

## 💾 Instruções de Instalação e Execução

### 1\. Preparação dos Arquivos

1.  Extraia o conteúdo do projeto em uma única pasta.
2.  Confirme que os arquivos Python (`main.py`, `dao.py`, `migracao.py`, `excecoes.py`, `logs.py`, etc.) e os arquivos JSON de exemplo (`*.json`) estão presentes.

### 2\. Inicialização do Banco de Dados (SQLite)

O sistema utiliza o banco de dados `seguros_sistema.db`. Ele será criado automaticamente.

  * **Aviso:** O banco de dados **não** deve ser mantido no GitHub, apenas o código.

### 3\. Rotina de Migração (Populando o Banco)

Para usar os dados de exemplo da Sprint 2 no novo banco SQLite, você deve rodar o script de migração **uma única vez**:

```bash
python migracao.py
```

*Após rodar este comando, o arquivo `seguros_sistema.db` será criado e preenchido com todos os dados dos seus `*.json`.*

### 4\. Execução do Sistema

Abra um terminal na pasta do projeto e inicie o sistema:

```bash
python main.py
```

### 🔑 Credenciais de Acesso (Persistidas no SQLite)

| Perfil | Usuário | Senha | Permissões |
| :--- | :--- | :--- | :--- |
| **Administrador** | admin | admin123 | Total: Cadastro, Edição, Cancelamento, Sinistros e Relatórios. |
| **Comum** | user | user123 | Apenas Consultas e Relatórios. |

-----

## 🔍 Entregáveis e Onde Encontrá-los

| Entregável | Onde está | Como Funciona |
| :--- | :--- | :--- |
| **Persistência SQLite** | Arquivo `seguros_sistema.db` | O módulo `dao.py` gerencia o CRUD (Create, Read, Update, Delete). |
| **Rotina de Migração** | Arquivo `migracao.py` | Lida com a criação do schema e importação dos JSONs. |
| **Auditoria e Logs** | **Pasta `logs/`** | Arquivos `.log` são gerados (ex: `auditoria_20241020.log`) e registram *quem* (`USUARIO: admin`) fez *o quê*. |
| **Tratamento de Erros** | Módulo `excecoes.py` | Exibe mensagens amigáveis na CLI (Ex: `ERRO: Apólice já está inativa.`) em vez de *stack traces*. |
| **Relatórios Novos** | Menu **11-Relatórios Avançados** | Implementação de **Receita Mensal Prevista**, **Ranking por Valor Segurado** e **Sinistros por Período**. |
| **Exportação CSV** | **Pasta `exports/`** | Após gerar os relatórios, o sistema pergunta se deseja exportar, salvando um arquivo CSV na pasta `exports/`. |

## 📃 Exemplos Rápidos de Uso

| Fluxo | Ação no Menu | O que Testar |
| :--- | :--- | :--- |
| **Teste de Auditoria** | Tente fazer Login com senha errada. | O console exibe o erro e o log registra um `WARNING` (Usuário: TENTATIVA). |
| **Cadastro com Log** | Login como `admin`. Opção **1-Cadastrar Cliente**. | O log registra um `INFO` com o CPF e nome do cliente cadastrado. |
| **Fluxo de Erro** | Login como `admin`. Opção **9-Cancelar Apólice** e tente cancelar o mesmo número duas vezes. | Na segunda tentativa, o console exibe `ERRO: Apólice [número] já está inativa.` |
| **Geração de CSV** | Opção **11-Relatórios Avançados**, depois **2-Ranking Clientes...** | No final do relatório, digite `s` para exportar. Verifique a criação do arquivo CSV na pasta `exports/`. |

## 🗃️ Estrutura de Arquivos Principal

  * **`main.py`**: Inicia o sistema e gerencia o menu principal.
  * **`dao.py`**: **NOVO:** Camada de Acesso a Dados (CRUD) que se comunica diretamente com o SQLite.
  * **`migracao.py`**: **NOVO:** Script para importar dados dos JSONs para o SQLite.
  * **`logs.py`**: **NOVO:** Configura o módulo de auditoria (`logging`).
  * **`excecoes.py`**: **NOVO:** Define as classes de erro de negócio.
  * **`sistema.py`**: Controlador que usa o `dao.py` para todas as operações e registra logs.
  * **`cliente.py`, `apolice.py`, `sinistro.py`, `seguro.py`**: Contêm as Classes POO (Modelos) e as funções de menu.
  * **`persistencia.py`**: Mantido para a função de **exportação** CSV/JSON.