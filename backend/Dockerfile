FROM python:3.11-alpine

WORKDIR /app

# Используем официальные репозитории Alpine с явным указанием версии
RUN echo "https://dl-cdn.alpinelinux.org/alpine/v3.19/main" > /etc/apk/repositories && \
    echo "https://dl-cdn.alpinelinux.org/alpine/v3.19/community" >> /etc/apk/repositories && \
    apk update --no-cache && \
    apk add --no-cache \
        libgl1-mesa-glx \
        libstdc++ \
        curl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]