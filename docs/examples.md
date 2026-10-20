# API examples (cURL)

> Requires running stack: `docker compose up -d`
> All examples assume `http://127.0.0.1:8000`.

## Health check

```bash
curl http://127.0.0.1:8000/health
```

```json
{"status":"ok"}
```

## Create a parse job

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"text": "python", "area": 1}'
```

```json
{
  "status": "pending",
  "id": 1,
  "text": "python",
  "area": 1,
  "items_count": 0,
  "created_at": "2026-10-20T09:19:56.273955Z"
}
```

## Get job status

```bash
curl http://127.0.0.1:8000/jobs/1
```

```json
{
  "status": "completed",
  "id": 1,
  "text": "python",
  "area": 1,
  "items_count": 30,
  "created_at": "2026-10-20T09:19:56.273955Z"
}
```

## Get resumes for a job

```bash
curl http://127.0.0.1:8000/jobs/1/resumes
```

```json
[
  {
    "external_id": "r001",
    "title": "Python-разработчик",
    "area_name": "Москва",
    "area_id": 1,
    "salary_amount": 180000,
    "salary_currency": "RUR",
    "url": "https://hh.ru/resume/r001",
    "work_format": ["Удалённо", "Гибрид"],
    "skills": ["Python", "Django", "PostgreSQL"]
  }
]
```

## Average salary

```bash
curl "http://127.0.0.1:8000/analytics/salary/average?area_id=1&keyword=python"
```

```json
{
  "area_id": 1,
  "keyword": "python",
  "average": 241666.67,
  "count": 6
}
```

## Median salary

```bash
curl "http://127.0.0.1:8000/analytics/salary/median?area_id=1&keyword=python"
```

```json
{
  "area_id": 1,
  "keyword": "python",
  "median": 210000.0,
  "count": 6
}
```

## Top skills

```bash
curl "http://127.0.0.1:8000/analytics/skills/top?area_id=1&limit=10"
```

```json
[
  {"skill": "Python", "count": 13},
  {"skill": "FastAPI", "count": 4},
  {"skill": "Docker", "count": 4},
  {"skill": "Django", "count": 3}
]
```

## Top skills — non-IT (povara)

```bash
curl "http://127.0.0.1:8000/analytics/skills/top?keyword=povar&limit=10"
```

```json
[
  {"skill": "Culinary", "count": 2},
  {"skill": "Baking", "count": 1},
  {"skill": "Team Management", "count": 1}
]
```

## Errors

```bash
# 404 — job not found
curl -i http://127.0.0.1:8000/jobs/999999

# 409 — resumes requested before completion
curl -i http://127.0.0.1:8000/jobs/1/resumes

# 422 — invalid request
curl -i -X POST http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"text": ""}'
```