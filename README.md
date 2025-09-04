# Test Task Backend

## Даталогическая модель

<img width="1233" height="865" alt="ER-диаграмма" src="https://github.com/user-attachments/assets/4792991f-116b-4c66-9108-0724390050e2" />

## SQL-запросы

### 2.1

```sql
SELECT 
    c.name AS client_name,
    COALESCE(SUM(oi.quantity * oi.price), 0) AS total_sum
FROM shop.client c
LEFT JOIN shop."order" o ON o.client_id = c.id
LEFT JOIN shop.order_item oi ON oi.order_id = o.id
GROUP BY c.name
ORDER BY total_sum DESC;
```

### 2.2

```sql
SELECT
  c.id,
  c.name,
  COUNT(child.id) AS children_count
FROM shop.category c
LEFT JOIN shop.category child ON child.parent_id = c.id
GROUP BY c.id, c.name
ORDER BY children_count DESC, c.name;
```

### 2.3.1



### 2.3.2



## Веб-приложение на **FastAPI + SQLAlchemy (async)** с PostgreSQL в качестве базы данных.  

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
