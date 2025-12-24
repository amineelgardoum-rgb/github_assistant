FROM python:3.11-slim 
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    --default-timeout=300 \
    --retries 10 \
    -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python","-u","main.py"]