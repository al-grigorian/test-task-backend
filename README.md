# Test Task Backend

Веб-приложение на **FastAPI + SQLAlchemy (async)** с PostgreSQL в качестве базы данных.  

## Стек технологий

- Python 3.12
- FastAPI
- SQLAlchemy (asyncio)
- PostgreSQL
- Docker + Docker Compose
- Poetry (управление зависимостями)

## Подготовка окружения

1. Скопируйте файл окружения:
   ```bash
   cp .env.example .env

## Собрать и запустить:

docker compose up --build -d

После успешного запуска:

- Бэкенд доступен по адресу: http://localhost:8000
- Swagger-документация API: http://localhost:8000/docs
- ReDoc-документация API: http://localhost:8000/redoc

## Основные эндпоинты:

POST /orders/{order_id}/add_item/