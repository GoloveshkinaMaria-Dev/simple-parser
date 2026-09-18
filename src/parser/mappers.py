from src.parser.domain.entities import Resume

from .schemas import HHResume, HHResumeSearchResponse


def hh_resume_to_domain(hh: HHResume) -> Resume:
    return Resume(
        id=hh.id,
        title=hh.title,
        first_name=hh.first_name,
        last_name=hh.last_name,
        area=hh.area.name if hh.area else "",
        salary_amount=hh.salary.amount if hh.salary else None,
        salary_currency=hh.salary.currency if hh.salary else None,
        url=hh.alternate_url,
        work_format=[wf.name for wf in hh.work_format] if hh.work_format else [],
    )


def hh_response_to_domain_list(response: HHResumeSearchResponse) -> list[Resume]:
    return [hh_resume_to_domain(item) for item in response.items]
