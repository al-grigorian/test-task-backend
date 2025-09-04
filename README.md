# Test Task Backend

## Даталогическая модель

<img width="1233" height="865" alt="ER-диаграмма" src="https://github.com/user-attachments/assets/4792991f-116b-4c66-9108-0724390050e2" />

## SQL-запросы

### Создание таблиц

```sql
CREATE SCHEMA IF NOT EXISTS shop;

CREATE TABLE shop.category (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INT REFERENCES shop.category(id) ON DELETE CASCADE
);

CREATE TABLE shop.product (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    price NUMERIC(10,2) NOT NULL,
    category_id INT REFERENCES shop.category(id) ON DELETE SET NULL
);

CREATE TABLE shop.client (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT
);

CREATE TABLE shop.order (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES shop.client(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE shop.order_item (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES shop."order"(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES shop.product(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    price NUMERIC(10,2) NOT NULL
);

```

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

```sql
CREATE OR REPLACE VIEW shop.top5_most_sold_last_month AS
WITH RECURSIVE category_tree AS (
    -- старт - все корневые категории (уровень 1)
    SELECT id, name, parent_id, id AS root_id, name AS root_name
    FROM shop.category
    WHERE parent_id IS NULL

    UNION ALL

    -- рекурсивно спускаемся вниз по дереву категорий, сохраняя корень (root_id, root_name)
    SELECT c.id, c.name, c.parent_id, ct.root_id, ct.root_name
    FROM shop.category c
    JOIN category_tree ct ON c.parent_id = ct.id
),
sales AS (
    -- суммируем проданные единицы по товарам за последний месяц
    SELECT oi.product_id, SUM(oi.quantity) AS total_qty
    FROM shop.order_item oi
    JOIN shop."order" o ON oi.order_id = o.id
    WHERE o.created_at >= now() - INTERVAL '1 month'
    GROUP BY oi.product_id
)
SELECT
    p.id AS product_id,
    p.name AS product_name,
    COALESCE(ct.root_name, 'Без категории') AS top_level_category,
    s.total_qty
FROM sales s
JOIN shop.product p ON p.id = s.product_id
LEFT JOIN category_tree ct ON ct.id = p.category_id
ORDER BY s.total_qty DESC
LIMIT 5;
```

Проверка результата:

```sql
SELECT * FROM shop.top5_most_sold_last_month;
```

### 2.3.2 Оптимизация

**Можно выделить несколько узких мест текущего запроса 2.3.1.**

**Рекурсивный CTE (category_tree):**
При большом числе категорий и частых запросах это может быть дорого и неэффективно.
CTE часто пересчитывает дерево при каждом выполнении запроса (а не использует кэш).

**Фильтр по created_at >= now() - interval '1 month':**
Если таблицы order или order_item становятся очень большими (тысячи заказов в день), этот фильтр будет сканировать значительную часть данных без индекса на created_at.

**Агрегация по order_item:**
Нужно быстро суммировать по product_id — при большом объёме важно иметь соответствующие индексы.

**Я могу предложить следующие варианты для оптимизации запроса и общей схемы данных для повышения производительности системы в условиях роста данных:**

**Создание индексов**
```sql
-- индекс для быстрого поиска заказов по дате
CREATE INDEX idx_order_created_at ON shop."order"(created_at);

-- индекс по связи order_item → order, так как часто используется при JOIN
CREATE INDEX idx_order_item_order_id ON shop.order_item(order_id);

-- индекс по product_id для быстрых агрегаций
CREATE INDEX idx_order_item_product_id ON shop.order_item(product_id);

-- индекс для быстрого получения родительской или дочерней категории
CREATE INDEX idx_category_parent_id ON shop.category(parent_id);

-- индекс по product.category_id для JOIN
CREATE INDEX idx_product_category_id ON shop.product(category_id);
```

**Денормализация**

Также можно использовать денормализацию для добавления в product колонки top_category_id и при добавлении или изменении категории продукта вычислять, например через триггер, и записывать туда корневую категорию. Тогда в запросе не нужен рекурсивный CTE и достаточно обычного join по product.top_category_id.

**Материализованное представление**

Еще вариант - создать материализованное представление с подсчитанной агрегацией продаж. Обновлять материализованное представление можно будет по расписанию или по какому-либо событию.

Например, можно сделать так:
```sql
CREATE MATERIALIZED VIEW shop.sales_month AS
SELECT
    oi.product_id,
    SUM(oi.quantity) AS total_qty
FROM shop.order_item oi
JOIN shop."order" o ON o.id = oi.order_id
WHERE o.created_at >= now() - interval '1 month'
GROUP BY oi.product_id;

```

**Партиционирование**

Для таблиц order и order_item можно сделать partition by range (created_at) — PostgreSQL тогда будет читать только последний раздел (например, 2025_09), а не всё сразу.

**Кеширование**

Для запросов, которые часто выполняются, можно отдавать результат из кеша Redis. Из плюсов такого способа можно выделить мгновенный ответ для часто запрашиваемых отчётов, а также снятие нагрузки с PostgreSQL. Но при этом данные могут быть немного устаревшими, но для аналитики это обычно не критично

## Веб-приложение на **FastAPI + SQLAlchemy (async)** с PostgreSQL в качестве базы данных.  

## Стек технологий

- Python 3.12
- FastAPI
- SQLAlchemy (asyncio)
- PostgreSQL
- Docker + Docker Compose
- Poetry (управление зависимостями)

## Подготовка окружения

Скопируйте файл окружения:
   ```bash
   cp .env.example .env
   ```
## Собрать и запустить:

```bash
docker compose up --build -d
```

После успешного запуска:

- Бэкенд доступен по адресу: http://localhost:8000
- Swagger-документация API: http://localhost:8000/docs
- ReDoc-документация API: http://localhost:8000/redoc

## Основные эндпоинты:

POST /orders/{order_id}/add_item/
