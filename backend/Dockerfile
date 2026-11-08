# API do JogoTeca (FastAPI). Construir:  docker build -t jogoteca-api backend
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Roda sem privilégios de administrador (boa prática de segurança)
RUN useradd --create-home --uid 10001 jogoteca && mkdir -p /srv/armazenamento/capas && chown -R jogoteca /srv
USER jogoteca

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=5 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/saude').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
