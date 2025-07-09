### 1. Клонируйте репозиторий и перейдите в папку

```bash
git clone <repo‑url>
cd <project‑dir>
```

### 2. Создайте виртуальное окружение и установите зависимости

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows CMD
.venv\Scripts\activate

pip install flask
```

### 3. Запустите сервис

```bash
python app.py
```

По умолчанию API доступно на **[http://localhost:5000](http://localhost:5000)**.

> При первом запуске создаётся файл `reviews.db` и таблица `reviews`.

---

## API

### POST `/reviews`

Добавляет отзыв и возвращает его вместе с определённым настроением.

**Запрос**

```json
{ "text": "Очень люблю ваш сервис" }
```

**cURL‑пример (PowerShell)**

```powershell
curl.exe -X POST http://localhost:5000/reviews `
  -H "Content-Type: application/json" `
  --data '{"text":"Очень люблю ваш сервис"}'
```

**Ответ `201 Created`**

```json
{
  "id": 1,
  "text": "Очень люблю ваш сервис",
  "sentiment": "positive",
  "created_at": "2025-07-09T12:03:45.123456"
}
```

---

### GET `/reviews?sentiment={value}`

Возвращает массив отзывов. Если указать `sentiment`, будут отфильтрованы только записи с соответствующим значением.

**Примеры**

```bash
# Все отзывы
curl http://localhost:5000/reviews

# Только negative
curl http://localhost:5000/reviews?sentiment=negative
```

---

## Как это работает

| Шаг | Описание                                                                                                                                                                |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | При импорте `app.py` выполняется `_init_db()` — создаёт базу, если её нет.                                                                                              |
| 2   | Класс **`SentimentClassifier`** содержит списки ключевых слов `POSITIVE` и `NEGATIVE` и метод `classify(text)`; если ни одно слово не найдено — возвращается `neutral`. |
| 3   | `POST /reviews` вызывает `SentimentClassifier.classify`, пишет отзыв в таблицу `reviews` и отдаёт JSON‑ответ.                                                           |
| 4   | `GET /reviews` выполняет `SELECT`, при наличии query‑параметра `sentiment` добавляет `WHERE sentiment = ?`.                                                             |

---
