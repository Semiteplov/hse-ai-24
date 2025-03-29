# 🔗 HW 8 FastAPI URL Shortener

Сервис для сокращения ссылок с аналитикой, регистрацией пользователей и кэшированием через Redis.

---

## 🚀 Возможности

- ✅ Сокращение длинных URL с генерацией короткого кода
- ✅ Кастомные алиасы (`custom_alias`)
- ✅ Ограничение по времени жизни ссылки (`expires_at`)
- ✅ Регистрация и авторизация (JWT)
- ✅ Статистика по ссылке (кол-во визитов, даты)
- ✅ Кэширование редиректов и популярности через Redis
- ✅ Очистка неиспользуемых и истёкших ссылок
- ✅ Поиск по оригинальному URL

---

## 📦 API Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/register` | Регистрация пользователя |
| `POST` | `/login` | Получение JWT токена |
| `POST` | `/links/shorten` | Создание короткой ссылки *(авторизация нужна)* |
| `GET` | `/links/{short_code}` | Редирект по короткой ссылке |
| `GET` | `/links/{short_code}/stats` | Статистика по ссылке |
| `GET` | `/links/search?original_url=...` | Поиск по оригинальному URL |
| `GET` | `/links/expired` | Список истёкших ссылок |
| `DELETE` | `/cleanup-unused-links?n_days=30` | Удалить неиспользуемые ссылки |
| `PUT` | `/links/{short_code}` | Обновить оригинальный URL |
| `DELETE` | `/links/{short_code}` | Удалить ссылку *(авторизация нужна)* |

---

## 🔐 Авторизация

1. Регистрация через `POST /register`  
2. Логин и получение токена через `POST /login`  
3. Заголовок для авторизации: `Authorization: Bearer <your_token>`

---

## 🧪 Примеры запросов

### 📝 Регистрация 
```bash
curl -X 'POST' \
  'http://localhost:8001/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "username",
  "password": "password"
}'
```

### 🔑 Авторизация 
```bash
curl -X 'POST' \
  'http://localhost:8001/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=login&password=password&scope=&client_id=string&client_secret=string'
```

### 🔗 Сократить ссылку
```bash
curl -X POST http://localhost:8001/links/shorten \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://example.com",
    "expires_at": "2025-04-01T12:00:00"
  }'
```

### 📊 Получить статистику
```bash
curl http://localhost:8001/links/abc123/stats
```

### 🔎 Поиск по оригинальному URL
```bash
curl "http://localhost:8001/links/search?original_url=https://example.com"
```

### 🧼 Очистка неиспользуемых ссылок
```bash
curl -X DELETE "http://localhost:8001/cleanup-unused-links?n_days=30"
```

---
## 🛠️ Запуск через Docker

### Шаг 1. Прописать envs при запуске компоуза, либо в файле `.env`, например
```yaml
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=shortener_db
REDIS_PORT=6379
REDIS_DB=0
```

### Шаг 2. Запуск контейнеров, пример с файлом
```bash
docker-compose --env-file .env up --build
```

Приложение будет доступно на:
http://localhost:8001 \
Документация: http://localhost:8001/docs

## 💾 Кэш (Redis)
Используется Redis для хранения популярных ссылок \
Кэширует short_code → original_url \
Кэш очищается при обновлении или удалении ссылки

---
## 🌐 Демо-сервер

Сервис развернут на личном VPS по адресу:

🔗 **http://185.250.45.224:8001/**  
📄 Swagger-документация: **http://185.250.45.224:8001/docs**

---

# 📌 Тестирование проекта

## 🛠 Установка зависимостей
```bash
pip install -r requirements-dev.txt
```

## 🚀 Запуск тестов из корня проекта и генерация отчёта о покрытии
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

## 📊 Просмотр отчёта
Открыть `htmlcov/index.html` в браузере.

