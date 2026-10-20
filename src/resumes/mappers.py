from src.parser.domain.entities import Resume
from src.resumes.models import ResumeORM  # , ResumeSkillORM


def resume_to_orm(resume: Resume, job_id: int) -> ResumeORM:
    """Convert a domain Resume to a ResumeORM row (skills are handled separately)."""
    return ResumeORM(
        job_id=job_id,
        external_id=resume.external_id,
        title=resume.title,
        area_id=resume.area_id,
        area_name=resume.area_name,
        salary_amount=resume.salary_amount,
        salary_currency=resume.salary_currency,
        url=resume.url,
        work_format=resume.work_format,
    )


def orm_to_resume(orm: ResumeORM) -> Resume:
    """Convert a ResumeORM row (with loaded skills) back to a domain Resume."""
    return Resume(
        external_id=orm.external_id,
        title=orm.title,
        first_name=None,
        last_name=None,
        area_name=orm.area_name,
        area_id=orm.area_id,
        salary_amount=orm.salary_amount,
        salary_currency=orm.salary_currency,
        url=orm.url,
        work_format=orm.work_format,
        skills=[s.skill for s in orm.skills],
    )
