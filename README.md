# simple-parser

[![CI](https://github.com/USERNAME/hh_parser/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/hh_parser/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-soon-lightgrey)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Парсер вакансий с [hh.ru](https://hh.ru).
Пет-проект, в котором я совмещаю **разработку** и **тестирование**:
чистая архитектура на стороне кода + pytest, моки, фикстуры, CI и Playwright
на стороне QA.

> **Статус:** проект в активной разработке. Ниже — публичный TODO-лист,
> который обновляется по мере продвижения.

---

## Зачем этот проект

Я откликаюсь на позиции **Junior Python Developer** и **Junior QA Engineer**.
Чтобы показать обе стороны, я делаю один проект, где видно:

- как я **пишу код** — модули, dataclass'ы, разделение слоёв, типизация;
- как я **тестирую код** — unit, integration, UI-тесты, моки, фикстуры, coverage;
- как я **организую процесс** — CI, документация, тест-кейсы, чек-листы.

---

## Что делает проект

1. Забирает вакансии с hh.ru по поисковому запросу.
2. Парсит сырой JSON в domain-модели.
3. Сохраняет результат в JSON / CSV / SQLite.
4. Умеет считать статистику: средняя зарплата, топ-навыков, распределение по компаниям.
5. Показывает результаты в простом веб-UI.

---

## Стек

**Разработка**
- Python 3.13
- `requests` — HTTP-клиент
- `dataclasses` — domain-модели
- `sqlite3` — хранилище (без ORM)
- `argparse` / `typer` — CLI

**Тестирование**
- `pytest` — фреймворк
- `pytest-mock` — моки
- `responses` — мок HTTP-слоя
- `pytest-cov` — покрытие
- `Playwright` — UI-тесты

**Инфраструктура**
- GitHub Actions — CI на каждый push
- `ruff` — линтер + форматтер
- `mypy` — статическая типизация

---
## Архитектура

Проект построен по принципам **Domain-Driven Design (DDD)** и следует
**best practices FastAPI** — слои разделены, домен изолирован от
инфраструктуры, границы приложения описаны через Pydantic.


### Ключевые решения

- **Domain — на `@dataclass`**, без Pydantic/SQLAlchemy. Чистый Python,
  легко тестируется, не зависит от фреймворков.
- **DTO — на Pydantic**, только на границе (request/response, конфиг).
- **Domain Events** — `@dataclass(frozen=True)`. Агрегат копит их в `_events`,
  Application Service публикует после `save`.
- **Repository** — `Protocol` в Domain, реализация — в Infrastructure.
- **Мапперы** между domain, DTO и ORM — отдельным слоем.
- **Dependency Injection** — через `Depends` FastAPI: репозиторий, сервис,
  HTTP-клиент.
---

## Быстрый старт

...

### Запуск тестов
...

---

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py                        # общие фикстуры проекта
└── parser/                            # тесты модуля parser
    ├── __init__.py
    ├── conftest.py                    # фикстуры: HHResume, HHArea, HHSalary, HHWorkFormat
    ├── fixtures/
    │   ├── hh_resume_one.json         # одно резюме (проверка HHResume отдельно)
    │   └── hh_resume_search.json      # обёртка ответа: 3 резюме (полное, без salary, без area)
    └── test_mappers.py                # unit-тесты hh_resume_to_domain и hh_response_to_domain_list
```
---
## TODO — публичный роадмап

`[ ]` — запланировано, `[~]` — в работе, `[x]` — готово.

### Этап 1. Базовая разработка
- [x] Структура проекта, `requirements.txt`
- [x] `.gitignore`, `.env.example`
- [x] `src/config.py` — `BaseSettings` (DATABASE_URL, REDIS_URL, ENVIRONMENT)
- [x] `src/main.py` — FastAPI app + `/health`
- [ ] `src/database.py` — async engine, `async_sessionmaker`, `get_session`
- [x] Скрытие docs в проде
- [ ] Глобальные exception хендлеры

### Этап 2. DTO + роутер
- [~] `src/jobs/schemas.py`
- [ ] `src/jobs/router.py` эндпоинты-заглушки
- [ ] Проверка в `/docs` (Swagger видит схемы и эндпоинты)

### Этап 3. Домен
- [ ] `src/jobs/domain/value_objects.py` — `JobStatus` (StrEnum)
- [ ] `src/jobs/domain/events.py`
- [ ] `src/jobs/domain/entities.py`
- [ ] `src/jobs/domain/exceptions.py`
- [x] `src/parser/domain/entities.py`
- [ ] Юнит-тесты домена:
  - [ ] переходы состояний
  - [ ] накопление событий

### Этап 4. Персистентность (ORM + репозиторий)
- [ ] `src/jobs/models.py` — SQLAlchemy ORM
- [ ] `src/jobs/repository.py`
- [ ] `src/jobs/infrastructure/repository.py`
- [ ] `src/jobs/mappers.py`
- [ ] Alembic:
  - [ ] `alembic init`
  - [ ] Настройка `env.py` под async engine
  - [ ] Первая миграция
  - [ ] Naming conventions для индексов/констрейнтов
  - [ ] `file_template = %(year)d-%(month).2d-%(day).2d_%(slug)s`
- [ ] Интеграционные тесты репозитория (SQLite `:memory:` или тестовая PostgreSQL)

### Этап 5. Парсер
- [x] `src/parser/schemas.py`
- [x] `src/parser/mappers.py`
- [ ] `src/parser/client.py`
- [ ] `src/parser/service.py`
- [ ] `src/parser/exceptions.py`
- [ ] Retry и таймауты
- [ ] Логирование через `logging`
- [x] Юнит-тесты парсера: `test_mappers.py`
- [ ] Юнит-тесты парсера: `test_search_all.py` — пагинация
- [ ] Негативные кейсы: пустой ответ, отсутствие `items`, битый JSON
- [ ] Тест клиента с моками:
  - [ ] 200 OK
  - [ ] 500 → retry
  - [ ] timeout → retry
  - [ ] 429 → backoff

### Этап 6. Application Service (use cases)
- [ ] `src/jobs/service.py` — `ParseJobService`:
  - [ ] создание задачи
  - [ ] возвращение задачи
  - [ ] запуск парсинга, сохранение, публикация событий
  - [ ] список результатов
- [ ] Юнит-тесты сервиса с фейковым репозиторием и фейковым парсером
- [ ] `src/jobs/dependencies.py`
- [ ] Замена заглушек в `router.py` на реальные вызовы сервиса
- [ ] Интеграционные тесты API
- [ ] `dependency_overrides` для подмены зависимостей в тестах

### Этап 7. Фоновые задачи (воркер)
- [ ] Redis + `arq` **или** Celery
- [ ] `src/workers/tasks.py` — `parse_job_task(job_id)`
- [ ] `src/workers/settings.py` — конфиг воркера
- [ ] `POST /jobs` теперь **ставит задачу в очередь**, а не парсит синхронно
- [ ] Публикация доменных событий после `save` (event bus)
- [ ] Логирование задач

### Этап 8. Тесты (полный набор)
- [ ] `tests/conftest.py`:
  - [ ] async client (`httpx.ASGITransport`)
  - [ ] тестовая БД (фикстура с транзакцией/откатом)
  - [ ] фейковый репозиторий
  - [ ] фейковый парсер
- [x] `tests/fixtures/` — сохранённые ответы hh.ru (JSON)
- [ ] Unit-тесты:
  - [ ] домен (без FastAPI)
  - [ ] парсер
  - [ ] сервис (с фейками)
- [ ] Integration-тесты:
  - [ ] API (роуты, статусы, ошибки)
  - [ ] репозиторий
  - [ ] воркер (с фейковым парсером)
- [ ] Негативные кейсы: 404, 409, 422, 500
- [ ] Покрытие ≥ 85%

### Этап 9. Инфраструктура
- [ ] GitHub Actions:
  - [ ] `pytest` на push/PR
  - [ ] `ruff check` + `ruff format --check`
  - [ ] `mypy`
  - [ ] `coverage` + бейдж
  - [ ] Сервисы в CI (PostgreSQL, Redis)
- [ ] Бейдж статуса CI в README
- [ ] `pre-commit` хуки:
  - [ ] `ruff`
  - [ ] `ruff-format`
  - [ ] `mypy`
  - [ ] проверка на `.env` в коммите
- [ ] `Dockerfile`:
  - [ ] multi-stage
  - [ ] non-root user
- [ ] `docker-compose.yml`:
  - [ ] `api` (FastAPI + uvicorn)
  - [ ] `worker` (arq/Celery)
  - [ ] `postgres`
  - [ ] `redis`

### Этап 10. Документация
- [x] README с описанием и TODO
- [ ] `docs/architecture.md` — схема слоёв (DDD + FastAPI best practices)
- [ ] `docs/test_cases.md` — таблица тест-кейсов
- [ ] `docs/checklist.md` — чек-лист ручного тестирования
- [ ] OpenAPI/Swagger примеры (`response_model`, `responses`, `examples`)
- [ ] `examples/` — примеры curl-запросов
- [ ] Playwright-тесты UI, если появится фронт
---

## Прогресс

Обновляю по ходу разработки. Коммиты отражают реальный прогресс,
TODO-лист — синхронизирован с задачами.

- **Начало проекта:** сентябрь 2026
- **Текущий этап:** 1-2

---
