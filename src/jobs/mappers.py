from src.parser.domain.entities import Resume
from src.parser.schemas import ResumeResponse


def resume_to_response(resume: Resume) -> ResumeResponse:
    return ResumeResponse(
        id=resume.id,
        title=resume.title,
        area=resume.area,
        salary_amount=resume.salary_amount,
        salary_currency=resume.salary_currency,
        url=resume.url,
        work_format=resume.work_format,
    )
