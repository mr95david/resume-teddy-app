# Resume Teddy App

Aplicação para processamento de currículos (résumés/CVs) com análise automatizada, extração de texto e geração de resumos profissionais utilizando **FastAPI**, **MongoDB** e **LocalAI**.

A arquitetura consiste em uma API composta por microsserviços que se integram a modelos de linguagem executados localmente e a um banco de dados não relacional MongoDB. O objetivo é apoiar a automação do processo de seleção de candidatos por meio da extração e análise estruturada das informações contidas nos documentos.

---

## Arquitetura da API e Microsserviços

Atualmente a API expõe **dois conjuntos principais de microsserviços**, totalizando **6 operações**:

### 1. Health & Monitoring Service

Responsável por verificar o status básico da aplicação e a conectividade com o banco de dados.

- `GET /`  
  Retorna um status simples da API, indicando se o serviço está em execução.

- `GET /info`  
  Fornece informações gerais da aplicação, como versão e ambiente atual (por exemplo, *development*).

- `GET /db-health`  
  Executa um *ping* na instância do **MongoDB** para verificar se há conectividade com o banco de dados.

> Esses endpoints são úteis para monitoramento, automação de deploy e verificação rápida de saúde da aplicação.

---

### 2. Document Processing Service (`/process`)

Conjunto de endpoints responsáveis por receber arquivos, processá-los e registrar o histórico de consultas.

- `GET /process/`  
  Lista **todas as consultas** já processadas e armazenadas na coleção `document_queries` do MongoDB, em ordem decrescente de data.

- `GET /process/last/{limit}`  
  Retorna apenas os **N últimos registros** (até um máximo de 5), permitindo inspecionar rapidamente os processamentos mais recentes.

- `POST /process/upload`  
  Endpoint principal da aplicação.  
  Responsável por:
  - Receber múltiplos arquivos (PDF, JPG, JPEG, PNG);
  - Validar a extensão de cada arquivo;
  - Realizar a **extração de texto** utilizando o pipeline de OCR (Tesseract + Popller) para conteúdos em português, inglês e espanhol;
  - Organizar e normalizar os dados extraídos;
  - Enviar o conteúdo consolidado para o **LocalAI**, que:
    - Responde a uma pergunta específica do usuário (`query`), **ou**
    - Gera um **resumo profissional** dos currículos quando nenhuma pergunta é informada;
  - Persistir no MongoDB um registro do processamento, seguindo o schema `QueryResponse`:
    - `user_id`
    - `request_id`
    - `query`
    - `resultado`
    - `timestamp`

O retorno desse endpoint é sempre um objeto no formato `QueryResponse`, contendo o resultado final gerado pelo modelo de linguagem.

---

## **Armazenamento de Dados**

A aplicação **não armazena o conteúdo integral dos currículos/CVs** enviados.  
No banco de dados MongoDB são registrados apenas:

- Metadados dos processamentos anteriores;
- Informações de controle e auditoria (por exemplo, `user_id`, `request_id`, `timestamp`);
- O **resultado processado** (`resultado`), em formato de texto estruturado.

Dessa forma, o foco é manter um histórico de consultas e respostas sem reter os documentos originais, contribuindo para a privacidade dos candidatos e a conformidade com boas práticas de segurança de dados.

---

## Docker – Guia Rápido de Inicialização

### Pré-requisitos
Antes de iniciar, certifique-se de ter:
* [Docker](https://www.docker.com/) instalado no sistema.
* Credenciais válidas de conexão com **MongoDB**.
* Chave de API para **LocalAI** (ou equivalente).

---

## Instalação e Execução

### 1.1. Configurar Variáveis de Ambiente

Como primeiro passo, copie o arquivo de exemplo e crie seu próprio `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` preenchendo com seus valores reais:

```env
# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB_NAME=your_db_name
MONGODB_USER=your_db_user
MONGODB_PASSWORD=your_db_password
MONGODB_AUTH_SOURCE=admin

# LocalAI
LOCALAI_BASE_URL=http://localhost:8080/v1
LOCALAI_MODEL_NAME=localai_model_name
LOCALAI_SECRET_KEY=your_localai_secret

# Process dependencies
TESSERACT_CMD=/your/path/tesseract
POPLLER_PATH=/usr/bin 
```

Recomendação: Evite incluir símbolos especiais desnecessários (# * ') dentro dos valores das variáveis para prevenir erros de leitura.

### 1.2. Construir a Imagem Docker

No diretório raiz do projeto, execute:

```bash
docker build -t resume-teddy-app:latest .
```

Este comando cria a imagem da aplicação.

### 1.3. Executar o Contêiner

Após construir a imagem, execute o contêiner utilizando o arquivo `.env` criado:

```bash
docker run -p 8000:8000 --env-file .env --name resume-app resume-teddy-app:latest
```

A aplicação estará disponível em: 

[http://localhost:8000](http://localhost:8000)

### 1.4. Verificação da Aplicação

**Documentação Interativa (Swagger UI)** — abra no navegador:

[Swagger UI](http://localhost:8000/docs)

**Endpoint de Verificação de Saúde (Health Check)**

[http://localhost:8000/info](http://localhost:8000/info)

## Desenvolvimento Local

Abaixo encontra-se um guia simples e direto para executar o projeto **Resume Teddy App** em ambiente local, sem o uso de Docker.  
Inclui instalação dos pacotes necessários, configuração do ambiente virtual com **UV**, definição das variáveis de ambiente e inicialização da API.

---

### 1. Pré-requisitos

Antes de iniciar o desenvolvimento local, verifique se possui instalado:

- **Python 3.10+**
- **uv** (gerenciador de ambientes e dependências)
- **Tesseract OCR**
- **poppler-utils**
- Acesso a uma instância **MongoDB** (local ou remota)

---

### 2. Instalar e configurar o ambiente com UV

#### **2.1 Criar o ambiente virtual**

No diretório raiz do projeto e ativar o ambiente:

```bash
uv venv
source .venv/bin/activate
```

#### **2.2 Instalar as dependências**

```bash
uv sync
```

Isso instalará todos os pacotes listados no pyproject.toml, incluindo:

- FastAPI
- motor (MongoDB driver)
- pdfplumber
- PyPDF2
- pdfminer
- pytesseract
- pdf2image
- requests
- loguru
- openai (para LocalAI)

Caso durante o uso surja a necessidade de novos pacotes, eles podem ser adicionados com:

```bash
uv add nome-do-pacote
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` baseado no arquivo de exemplo:

```bash
cp .env.example .env
```

Edite os valores no arquivo `.env` conforme o seu ambiente:

```env
# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB_NAME=resume_db
MONGODB_USER=admin
MONGODB_PASSWORD=senha
MONGODB_AUTH_SOURCE=admin

# LocalAI
LOCALAI_BASE_URL=http://localhost:8080/v1
LOCALAI_MODEL_NAME=llama-3-8b-instruct-q4
LOCALAI_SECRET_KEY=dummy-key

# Dependências externas
TESSERACT_CMD=/usr/bin/tesseract
POPLLER_PATH=/usr/bin
```

#### Certifique-se de que:
- O Tesseract esteja acessível no caminho configurado.
- O Poppler esteja instalado e funcional.
- O LocalAI esteja rodando (caso deseje usar processamento com modelos).

### 4. Executar o servidor FastAPI localmente

Com o ambiente virtual ativado, execute o seguinte comando:

```bash
uvicorn app.main:app --reload --port 8000
```

A API estará acessível em: http://localhost:8000

## Notas Adicionais

- A aplicação utiliza Python 3.10.
- As dependências são gerenciadas usando `uv`.
- O servidor web é baseado em FastAPI + Uvicorn.
- OCR realizado com Tesseract, com suporte a inglês, espanhol e outros idiomas conforme configurado.
- LocalAI foi utilizado como mecanismo LLM local para geração de resumos. Guia oficial: https://localai.io/
