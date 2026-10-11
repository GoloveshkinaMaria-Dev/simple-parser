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

## Что делает проект

1. Забирает вакансии с hh.ru по поисковому запросу.
2. Парсит сырой JSON в domain-модели.
3. Сохраняет результат в PostgreSQL.
4. Умеет считать статистику: средняя зарплата по городам, медианная зарплата по городам, топ-навыков
5. Показывает результаты в простом веб-UI.

---

## Стек

**Разработка**
- Python 3.13
- **FastAPI**
- **Pydantic v2** + `pydantic-settings`
- **SQLAlchemy 2.0 (async)** + `asyncpg`
- **Alembic**
- `httpx`
- `dataclasses`
- **Celery**
- **Redis**
- **PostgreSQL**

**Тестирование**
- `pytest` + `pytest-asyncio`
- `pytest-mock`
- `respx`
- `pytest-cov`
- `httpx.ASGITransport`
- `Playwright`

**Инфраструктура**
- Docker + docker-compose
- GitHub Actions
- `ruff`
- `mypy`

---
## Архитектура

Проект построен по принципам **Domain-Driven Design (DDD)** и следует
**best practices FastAPI** — слои разделены, домен изолирован от
инфраструктуры, границы приложения описаны через Pydantic.


## Быстрый старт

...

### Запуск тестов
...

---

## Структура тестов

```
tests/
├── __init__.py
├── parser/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   │   ├── hh_resume_one.json
│   │   └── hh_resume_search.json
│   └── test_mappers.py
├── workers/
│   ├── __init__.py
│   ├── test_tasks.py           
│   └── test_build_service.py     
└── jobs/
    ├── __init__.py
    ├── conftest.py
    ├── test_mappers.py
    ├── test_jobs_api.py
    ├── test_repository.py
    └── test_parse_job.py           
  
```
---
## TODO — публичный роадмап

`[ ]` — запланировано, `[~]` — в работе, `[x]` — готово.

### Этап 1. Базовая разработка
- [x] Структура проекта, `requirements.txt`
- [x] `.gitignore`, `.env.example`
- [x] `src/config.py` — `BaseSettings` (DATABASE_URL, REDIS_URL, ENVIRONMENT)
- [x] `src/main.py` — FastAPI app + `/health`
- [x] `src/database.py` — async engine, `async_sessionmaker`, `get_session`
- [x] Скрытие docs в проде
- [x] Глобальные exception хендлеры

### Этап 2. DTO + роутер
- [x] `src/jobs/schemas.py`
- [x] `src/jobs/router.py` эндпоинты-заглушки
- [x] Проверка в `/docs` (Swagger видит схемы и эндпоинты)

### Этап 3. Домен
- [x] `src/jobs/domain/value_objects.py` — `JobStatus` (StrEnum)
- [x] `src/jobs/domain/events.py`
- [x] `src/jobs/domain/entities.py`
- [x] `src/jobs/domain/exceptions.py`
- [x] `src/parser/domain/entities.py`
- [x] Юнит-тесты домена:
  - [x] переходы состояний
  - [x] накопление событий

### Этап 4. Персистентность (ORM + репозиторий)
- [x] `src/jobs/models.py` — SQLAlchemy ORM
- [x] `src/jobs/repository.py`
- [x] `src/jobs/infrastructure/repository.py`
- [x] `src/jobs/mappers.py`
- [~] Alembic:
  - [x] `alembic init`
  - [x] Настройка `env.py` под async engine
  - [x] Первая миграция
  - [~] Naming conventions для индексов/констрейнтов
  - [~] `file_template = %(year)d-%(month).2d-%(day).2d_%(slug)s`
- [x] Интеграционные тесты репозитория (SQLite `:memory:` или тестовая PostgreSQL)

### Этап 5. Парсер
- [x] `src/parser/schemas.py`
- [x] `src/parser/mappers.py`
- [x] `src/parser/service.py`
- [x] `src/parser/exceptions.py`
- [x] Юнит-тесты парсера: `test_mappers.py`
- [x] Юнит-тесты парсера: `test_search_all.py`
- [x] Негативные кейсы: пустой ответ, отсутствие `items`, битый JSON


### Этап 6. Application Service (use cases)
- [x] `src/jobs/service.py` — `ParseJobService`:
  - [x] создание задачи
  - [x] возвращение задачи
  - [x] запуск парсинга, сохранение, публикация событий
  - [x] список результатов
- [x] Юнит-тесты сервиса
- [x] `src/jobs/dependencies.py`
- [x] Замена заглушек в `router.py` на реальные вызовы сервиса
- [x] Интеграционные тесты API

### Этап 7. Фоновые задачи (воркер)
- [x] Redis + `arq`
- [x] `src/workers/tasks.py` — `parse_job_task(job_id)`
- [x] `src/workers/settings.py` — конфиг воркера
- [x] `POST /jobs` теперь **ставит задачу в очередь**, а не парсит синхронно
- [x] Публикация доменных событий после `save` (event bus)
- [x] Логирование задач

### Этап 8. Аналитика: резюме в БД и агрегаты по зарплатам, навыкам

#### 8.1. Модель и хранение

- [~] `src/resumes/models.py` — `ResumeORM`:
- [~] Alembic-миграция

#### 8.2. Домен и мапперы

- [~] `src/resumes/mappers.py` — `resume_to_orm` / `orm_to_resume`
- [~] добавить skills в `Resume` и в маппер
- [~] Юнит-тесты мапперов

#### 8.3. Репозиторий

- [ ] `src/resumes/repository.py` — Protocol:
  - [ ] save_many
  - [ ] list_by_job
  - [ ] average_salary
  - [ ] median_salar
  - [ ] top_skills

- [ ] `src/resumes/infrastructure/repository.py` + `SqlResumeRepository`

#### 8.4. Интеграция с парсером и воркером

- [ ] `ParserService.search_all()` возвращает реальные `list[Resume]`
- [ ] `ParseJobService.__init__` принимает `resume_repo`

#### 8.5. Эндпоинт `GET /jobs/{id}/resumes`

- [ ] Заменить заглушку `return []` на `resume_repo.list_by_job(job_id)`
- [ ] `ResumeResponse.from_domain_list` корректно маппит реальные данные
- [ ] Тесты API: `200` + список, `409` для `pending`/`running`, `404` для несуществующего job

#### 8.6. Аналитика — сервис и DTO

- [ ] `src/analytics/domain/entities.py` — `SalaryStats`
- [ ] `src/analytics/schemas.py` — `SalaryStatsResponse`
- [ ] `src/analytics/service.py` — `AnalyticsService`
- [ ] `src/analytics/dependencies.py` — сборка сервиса
- [ ] `src/analytics/router.py` — эндпоинты:
  - [ ] `GET /analytics/salary/average?area=1&keyword=python`
  - [ ] `GET /analytics/salary/median?area=1&keyword=python`
  - [ ] `GET /analytics/salary/stats?area=1&keyword=python`
- [ ] Подключение роутера в `main.py`
- [ ] Нормализация `area` (int-код hh)
- [ ] Что делать с `salary_amount IS NULL -- подумать
- [ ] Что делать с разными валютами (`WHERE salary_currency = 'RUR'` или конвертация) -- подумать

#### 8.7. Тесты аналитики

- [ ] Unit-тесты `AnalyticsService` с фейковым репозиторием
- [ ] Интеграционные тесты репозитория
- [ ] API-тесты эндпоинтов аналитики
- [ ] Фикстура `resumes`

#### 8.8. Документация

- [ ] `docs/analytics.md` — какие метрики считаем, как интерпретировать
- [ ] Примеры запросов

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
---

## Прогресс

Обновляю по ходу разработки. Коммиты отражают реальный прогресс,
TODO-лист — синхронизирован с задачами.

- **Начало проекта:** сентябрь 2026
- **Текущий этап:** аналитика
---
