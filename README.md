# Resume Teddy App

Aplicação para processamento de currículos (résumés/CVs) com análise automatizada, extração de texto e geração de resumos profissionais utilizando **FastAPI**, **MongoDB** e **LocalAI**.

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

[Instrucciones de desarrollo sin Docker...]

## Notas Adicionais

- A aplicação utiliza Python 3.10.
- As dependências são gerenciadas usando `uv`.
- O servidor web é baseado em FastAPI + Uvicorn.
- OCR realizado com Tesseract, com suporte a inglês, espanhol e outros idiomas conforme configurado.
- LocalAI foi utilizado como mecanismo LLM local para geração de resumos. Guia oficial: https://localai.io/
