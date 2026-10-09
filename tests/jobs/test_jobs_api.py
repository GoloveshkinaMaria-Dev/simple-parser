from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_create_job_returns_202(client: AsyncClient):
    response = await client.post("/jobs", json={"text": "python", "area": 1})

    assert response.status_code == 202
    body = response.json()
    assert body["id"] == 1
    assert body["text"] == "python"
    assert body["status"] == "pending"
    assert body["items_count"] == 0
    assert "created_at" in body


async def test_create_job_without_text_returns_422(client: AsyncClient):
    response = await client.post("/jobs", json={"area": 1})

    assert response.status_code == 422


async def test_create_job_with_empty_text_returns_422(client: AsyncClient):
    response = await client.post("/jobs", json={"text": "", "area": 1})

    assert response.status_code == 422


async def test_create_job_with_invalid_per_page_returns_422(client: AsyncClient):
    response = await client.post("/jobs", json={"text": "python", "per_page": 999})

    assert response.status_code == 422


async def test_get_job_returns_created(client: AsyncClient):
    created = await client.post("/jobs", json={"text": "python", "area": 1})
    job_id = created.json()["id"]

    response = await client.get(f"/jobs/{job_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == job_id
    assert body["text"] == "python"
    assert body["status"] == "pending"


async def test_get_missing_job_returns_404(client: AsyncClient):
    response = await client.get("/jobs/999999")

    assert response.status_code == 404
    body = response.json()
    assert "999999" in body["detail"]


async def test_get_resumes_for_pending_returns_409(client: AsyncClient):
    created = await client.post("/jobs", json={"text": "python", "area": 1})
    job_id = created.json()["id"]

    response = await client.get(f"/jobs/{job_id}/resumes")

    assert response.status_code == 409
    assert str(job_id) in response.json()["detail"]


async def test_get_resumes_for_missing_job_returns_404(client: AsyncClient):
    response = await client.get("/jobs/999999/resumes")

    assert response.status_code == 404


async def test_get_resumes_for_completed_returns_empty_list(
    client: AsyncClient, session: AsyncSession
):
    created = await client.post("/jobs", json={"text": "python", "area": 1})
    job_id = created.json()["id"]

    await session.execute(
        text(
            "UPDATE parse_job SET status = 'completed', items_count = 0 WHERE id = :id"
        ),
        {"id": job_id},
    )
    await session.commit()

    response = await client.get(f"/jobs/{job_id}/resumes")

    assert response.status_code == 200
    assert response.json() == []
