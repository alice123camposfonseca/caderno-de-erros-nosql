# 📚 Caderno de Erros

Aplicação desenvolvida para a disciplina **Banco de Dados NoSQL**, do curso de Gestão da Informação da Universidade Federal de Uberlândia (UFU).

O Caderno de Erros ajuda estudantes a registrar, organizar e revisar erros cometidos durante os estudos, acompanhando suas dificuldades e seu histórico de revisões.

## 🎯 Objetivo

Evitar que erros cometidos em provas, listas e atividades fiquem esquecidos ou dispersos em anotações. O sistema permite registrar cada dificuldade e acompanhar as revisões realizadas.

## ✨ Funcionalidades

- **Cadastrar erros:** registrar matéria, assunto, tipo, descrição, dificuldade e tags.
- **Consultar erros:** visualizar os registros e filtrar por matéria, tipo e dificuldade.
- **Revisar erros:** selecionar um erro e registrar se acertou ou errou novamente.
- **Histórico de revisões:** consultar datas, resultados e observações de revisões anteriores.
- **Indicadores:** visualizar a quantidade de erros cadastrados e revisões realizadas.

## 🖥️ Tecnologias

- **Python** — linguagem de programação.
- **Streamlit** — interface da aplicação.
- **FastAPI** — API responsável pelas operações do sistema.
- **MongoDB Atlas** — banco de dados NoSQL orientado a documentos.
- **PyMongo** — comunicação entre Python e MongoDB.
- **python-dotenv** — carregamento de variáveis de ambiente.

## 🗂️ Organização do repositório

```
caderno-de-erros-nosql/
├── api/
│   └── main.py
├── database/
│   ├── criar_banco.py
│   └── ...
├── frontend/
│   └── app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 🧠 Por que MongoDB?

O MongoDB foi escolhido por ser um banco NoSQL orientado a documentos, que armazena dados em estruturas semelhantes a JSON.

Essa abordagem é adequada ao Caderno de Erros porque cada erro possui informações próprias e pode conter um conjunto variável de revisões. O histórico de revisões é armazenado como um **array de documentos embutidos** no documento do erro, representando naturalmente essa relação.

A flexibilidade do modelo permite acrescentar informações ao registro conforme novas funcionalidades forem desenvolvidas. Além disso, o projeto utiliza operações próprias do MongoDB, como:

- **Inserção:** `insert_one()`, para cadastrar erros.
- **Consulta:** `find()`, para recuperar os registros.
- **Atualização:** `update_one()`, com `$push` para adicionar revisões ao histórico.
- **Atualização numérica:** `$inc`, para incrementar a quantidade de erros quando o estudante erra novamente.

## 📄 Estrutura dos documentos

Um documento da coleção `erros` pode conter:

- `usuarioEmail`
- `materia`
- `assunto`
- `tipo`
- `descricao`
- `dificuldade`
- `tags`
- `quantidadeErros`
- `status`
- `dataCriacao`
- `revisoes` — array com data, resultado e observação de cada revisão.

## ⚙️ Como executar localmente

### 1. Pré-requisitos

- Python instalado.
- Acesso ao projeto no GitHub.
- Conta e cluster no MongoDB Atlas.

### 2. Instalar dependências

Na pasta raiz do projeto, crie e ative um ambiente virtual. Em seguida, instale as dependências:

```bash
pip install -r requirements.txt
```

Se houver um arquivo de dependências específico da pasta `database`, consulte também o respectivo `requirements.txt`.

### 3. Configurar o MongoDB

Crie um arquivo `.env` na raiz do projeto e configure sua string de conexão:

```env
MONGODB_URI=sua_string_de_conexao_do_mongodb_atlas
```

**Não compartilhe nem publique o arquivo `.env`.** O arquivo `.env.example` serve apenas como modelo de configuração.

### 4. Preparar o banco

Execute, conforme necessário, os scripts da pasta `database` para criar o banco, as coleções, os índices e os documentos de exemplo.

### 5. Iniciar a API

Na raiz do projeto:

```bash
uvicorn api.main:app --reload
```

A documentação interativa da API fica disponível em:

```
http://127.0.0.1:8000/docs
```

### 6. Iniciar a interface

Em outro terminal, na raiz do projeto:

```bash
streamlit run frontend/app.py
```

A interface será aberta em:

```
http://localhost:8501
```

> A aplicação é executada localmente. Para acessar em outro computador, é necessário configurar e executar a API e a interface nesse ambiente também.

## 🖼️ Capturas de tela

As capturas de tela da aplicação serão adicionadas nesta seção para apresentar as páginas **Início**, **Cadastrar erro**, **Consultar erros** e **Revisar erros**.

## 👥 Trabalho acadêmico

Projeto desenvolvido em dupla para a disciplina **Banco de Dados NoSQL**, na Universidade Federal de Uberlândia (UFU).
