# Gantt AI

AI-powered система управления проектами на основе диаграммы Ганта.
Проект позволяет создавать, редактировать и анализировать задачи через интерактивную Gantt-диаграмму и подключать AI-модель для работы с проектными данными.

## Возможности

### Gantt управление

* Интерактивная диаграмма Ганта
* Создание и редактирование задач
* Изменение:

  * названия задачи
  * даты начала
  * длительности
  * прогресса
  * исполнителя
  * связей между задачами
* Поддержка иерархии задач (parent/child)

### AI Assistant

AI-чат умеет работать с контекстом проекта:

* получает список текущих задач
* анализирует структуру проекта
* помогает планировать работу
* отвечает по состоянию проекта
* может использовать данные Gantt как контекст

Пример передаваемого контекста:

```json
{
  "project": {
    "name": "Gantt AI Project"
  },
  "tasks": [
    {
      "id": 1,
      "text": "Разработка продукта",
      "type": "summary",
      "assignee": "Команда",
      "progress": 0
    }
  ]
}
```

---

# Архитектура

```
gantt-ai
│
├── frontend
│   ├── React
│   ├── TypeScript
│   ├── TailwindCSS
│   └── Gantt UI
│
├── backend
│   ├── FastAPI
│   ├── API routes
│   ├── AI services
│   └── Business logic
│
└── docker-compose.yml
```

---

# Стек технологий

## Frontend

* React
* TypeScript
* Vite
* TailwindCSS
* @svar-ui/react-gantt
* shadcn/ui

## Backend

* Python
* FastAPI
* Pydantic
* HTTPX
* AI API integration

## Infrastructure

* Docker
* Docker Compose

---

# Запуск проекта

## Требования

Необходимо установить:

* Docker
* Docker Compose

Проверка:

```bash
docker --version
docker compose version
```

---

# Установка

Клонировать проект:

```bash
git clone <repository-url>

cd gantt-ai
```

---

# Настройка Backend

Создать файл:

```
backend/.env
```

Добавить переменные:

```env
OPENROUTER_API_KEY=your_api_key
```

Пример:

```env
OPENROUTER_API_KEY=xai-xxxxxxxxxxxxxxxx
```

---

# Запуск через Docker

Из корня проекта:

```bash
docker compose up -d --build
```

После запуска:

Frontend:

```
http://localhost:5173
```

Backend:

```
http://localhost:8000
```

Swagger API:

```
http://localhost:8000/docs
```

---

# API

## Получить задачи

```
GET /tasks
```

Возвращает текущий список задач Gantt.

---

## Загрузка Excel

```
POST /upload-excel
```

Импорт задач из Excel.

---

## Экспорт Excel

```
GET /export-excel
```

Экспорт проекта в Excel.

---

## AI Chat

```
POST /chat
```

Пример запроса:

```json
{
  "message": "Какие задачи просрочены?",
  "context": {
    "tasks": []
  }
}
```

Ответ:

```json
{
  "answer": "..."
}
```

---

# Структура Backend

```
backend/app

├── api
│   ├── chat.py
│   ├── tasks.py
│   ├── upload_excel.py
│   └── export_excel.py
│
├── data
│   └── seed_tasks.py
├── services
│   └── ai.py
│   └── mcp.py
│   └── mparser.py
│
├── schemas
└── chat.py
│
├── core
│   └── cors.py
├── state
│   └── gantt_state.py
│
└── main.py
```

---

# AI Integration

AI вынесен в отдельный сервис:

```
services/grok.py
```

Frontend не работает напрямую с AI.

Архитектура:

```
React
 |
 | POST /chat
 |
FastAPI
 |
 |
services/grok.py
 |
 |
xAI API
```

Такой подход позволяет:

* скрыть API ключ
* менять AI провайдера
* добавлять новую логику обработки контекста

---

# Переменные окружения

## Backend

| Переменная   | Назначение   |
| ------------ | ------------ |
| GROK_API_KEY | API ключ xAI |

## Frontend

| Переменная   | Назначение      |
| ------------ | --------------- |
| VITE_API_URL | URL backend API |

Пример:

```env
VITE_API_URL=http://localhost:8000
```

---

# Разработка

## Перезапуск backend

```bash
docker compose restart backend
```

## Логи backend

```bash
docker logs gantt-backend
```

## Вход в контейнер

```bash
docker exec -it gantt-backend sh
```

---

# Принципы архитектуры

Проект построен с разделением ответственности:

## Frontend

Отвечает за:

* UI
* взаимодействие пользователя
* отображение Gantt
* отправку запросов

## Backend

Отвечает за:

* API
* бизнес-логику
* обработку данных
* интеграцию AI

## AI Service

Отдельный слой:

```
services/
```

Не зависит от UI и API.

---

# Планируемые улучшения

* [ ] Авторизация пользователей
* [ ] Сохранение проектов в БД
* [ ] PostgreSQL
* [ ] История изменений задач
* [ ] AI генерация проекта из ТЗ
* [ ] Автоматическое распределение задач
* [ ] Анализ рисков проекта
* [ ] MCP интеграция
* [ ] Поддержка нескольких AI моделей

---

# License

MIT
