FROM python:3.11-slim 
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install \
    --default-timeout=300 \
    --retries 10 \
    -r requirements.txt

COPY . .
ENV  port=8000
ENV ENV=production
ENV HOST=0.0.0.0
CMD ["python","-u","main.py"]