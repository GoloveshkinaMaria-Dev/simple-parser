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

1. Забирает вакансии с hh.ru по поисковому запросу (например, `"Python разработчик"`).
2. Парсит сырой JSON в domain-модели (`Vacancy`).
3. Сохраняет результат в JSON / CSV / SQLite.
4. Умеет считать статистику: средняя зарплата, топ-навыков, распределение по компаниям.
5. Показывает результаты в простом веб-UI.

---

## Стек

**Разработка**
- Python 3.12
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

...в процессе...

---

## Быстрый старт

...

### Запуск тестов
...

---

## Структура тестов

```
...
```

Подход:

- **Парсер** тестируется без моков — на вход dict, на выход dataclass.
- **Клиент** тестируется с моками `requests.Session.get` и через `responses`.
- **Storage** — на `:memory:` SQLite, изоляция между тестами.
- **UI** — Playwright, только по маркеру `e2e`, чтобы не тормозить CI.

---

## TODO — публичный роадмап

`[ ]` — запланировано, `[~]` — в работе, `[x]` — готово.

### Этап 1. Базовая разработка
- [ ] Структура проекта, `pyproject.toml`, `requirements.txt`
- [ ] `models.py` — dataclass `Vacancy`
- [ ] `client.py` — HTTP-клиент hh.ru
- [ ] `parser.py` — `parse_vacancy` / `parse_vacancies`
- [ ] `storage.py` — сохранение в JSON
- [ ] `storage.py` — сохранение в CSV
- [ ] `storage.py` — сохранение в SQLite
- [ ] `cli.py` — CLI на `argparse`
- [ ] Пагинация (`search_all`) с лимитом страниц
- [ ] Статистика: средняя ЗП, топ-навыков
- [ ] Логирование через `logging`
- [ ] Retry на 5xx и таймауты (`tenacity` или `HTTPAdapter`)

### Этап 2. Тесты
- [x] `conftest.py` — фикстуры
- [x] `tests/fixtures/` — сохранённые ответы hh.ru
- [x] `test_parser.py` — unit-тесты парсера
- [x] `test_parser.py` — параметризация для `salary_avg`
- [~] `test_client.py` — мок `Session.get` через `pytest-mock`
- [ ] `test_client.py` — сценарии через `responses` (200, 500, timeout)
- [ ] `test_storage.py` — SQLite `:memory:`
- [ ] Тест на `__post_init__` (валидация `salary_from <= salary_to`)
- [ ] Негативные кейсы: пустой ответ, отсутствие `items`, битый JSON
- [ ] Покрытие ≥ 85%

### Этап 3. Инфраструктура
- [x] GitHub Actions: `pytest` на push/PR
- [ ] GitHub Actions: `ruff check` + `mypy`
- [ ] GitHub Actions: `coverage` + бейдж
- [ ] Бейдж статуса CI в README
- [ ] `pre-commit` хуки

### Этап 4. UI (опционально)
- [ ] Простой веб-UI (Flask + Jinja2 или статичный HTML)
- [ ] Playwright + Page Object Model
- [ ] E2E-тест: поиск → результат → пагинация
- [ ] Скриншоты UI в README

### Этап 5. Документация и «вау»
- [x] README с описанием и TODO
- [ ] `docs/test_cases.md` — таблица тест-кейсов
- [ ] `docs/checklist.md` — чек-лист ручного тестирования
- [ ] `docs/architecture.md` — схема слоёв
- [ ] Allure-отчёт по тестам
- [ ] Docker-образ
- [ ] Примеры в `examples/`

---

## Прогресс

Обновляю по ходу разработки. Коммиты отражают реальный прогресс,
TODO-лист — синхронизирован с задачами.

- **Начало проекта:** сентябрь 2026
- **Текущий этап:** 0 → 1 (планирую проект, начинаю писать модели)
- **Ближайшая цель:** закрыть этапы 1, 2 и подключить coverage в CI

---
