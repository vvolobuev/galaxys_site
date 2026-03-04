FROM python:3.11-alpine3.19

WORKDIR /app

RUN sed -i 's/dl-cdn.alpinelinux.org/mirror.yandex.ru/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache \
        libgl1-mesa-glx \
        libstdc++ \
        curl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]