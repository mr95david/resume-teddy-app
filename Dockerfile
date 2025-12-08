# Imagem oficial do Python 3.10
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para OCR e processamento de PDFs
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Instalar o uv (gerenciador de pacotes)
RUN pip install --no-cache-dir uv

# Copiar arquivos de configuração primeiro (para aproveitar o cache do Docker)
COPY pyproject.toml uv.lock ./

# Instalar dependências com o uv
RUN uv sync --frozen

# Copiar o restante do código
COPY . .

# Expor a porta para o FastAPI (8000 é a porta padrão do uvicorn)
EXPOSE 8000

# Comando padrão para executar a aplicação com uvicorn
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]