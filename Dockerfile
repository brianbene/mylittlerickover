FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./app.py
COPY rickover.jpg ./
COPY atom.jpg ./
COPY vertex_ai_config.json ./

ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

EXPOSE $PORT

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]