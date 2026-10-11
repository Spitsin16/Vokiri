# Vokiri

Vokiri — приложение для изучения английских слов через личный словарь, повторения и чтение. Пользователь сохраняет нужное значение слова, возвращается к нему по расписанию и встречает его в текстах своего уровня.

## MVP

- регистрация и JWT-авторизация;
- англо-русский поиск по словарю;
- выбор готового или добавление собственного перевода;
- личный словарь пользователя;
- ежедневные карточки и свободное повторение;
- планирование повторений по истории ответов;
- AI-тексты уровня A2, B1 и B2 со словами пользователя;
- изменение уровня текста с сохранением темы и подсветкой изучаемых слов.

## Статус

Готово:

- авторизация и получение текущего пользователя;
- импорт FreeDict;
- поиск слов, значений и переводов на английском и русском;
- добавление, получение, удаление и повторная активация слов;
- собственные переводы;
- миграции Alembic и базовая обработка ошибок.

Дальше: карточки, алгоритм повторений, AI-генерация текстов и подключение интерфейса к API. Папка `dist/` пока содержит визуальный прототип.

## Технологии

Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic, SQLite, JWT, Argon2 и pytest.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
```

Создайте `.env` в корне проекта:

```dotenv
SECRET_KEY=replace-with-a-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

```bash
python -m alembic upgrade head
python -m backend.importers.freedict_loader
python -m uvicorn backend.main:app --reload
```

Swagger: <http://127.0.0.1:8000/docs>

## Тесты

```bash
python -m pytest backend/tests
```

## Словарные данные

Англо-русский словарь предоставлен [FreeDict](https://freedict.org/) по лицензии CC BY-SA 3.0. Текст лицензии находится в `backend/data/raw/COPYING-FreeDict`.
