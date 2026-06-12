from __future__ import annotations

import math
import re
from datetime import datetime
from typing import Any

import pandas as pd

from src.clusters import classify_cluster
from src.skills import extract_skills


STANDARD_COLUMNS = [
    "job_id",
    "title",
    "company",
    "description",
    "city",
    "district",
    "country",
    "location",
    "remote_type",
    "experience",
    "seniority",
    "job_type",
    "salary_min",
    "salary_max",
    "salary_period",
    "salary_monthly_min",
    "salary_monthly_max",
    "education",
    "source_platform",
    "source_url",
    "source_updated_at",
    "fetched_at",
    "skills",
    "career_cluster",
]


def normalize_taiwanjobs(records: list[dict[str, Any]], *, fetched_at: str, source_updated_at: str | None) -> pd.DataFrame:
    rows = []
    for record in records:
        title = clean_text(record.get("OCCU_DESC（職務名稱）"))
        description = clean_text(record.get("JOB_DETAIL（工作內容）"))
        location = clean_text(record.get("CITYNAME（工作地點）"))
        city, district = split_taiwan_location(location)
        salary_min = parse_number(record.get("NT_L（薪資範圍下限）"))
        salary_max = parse_number(record.get("NT_U（薪資範圍上限）"))
        period = normalize_salary_period(record.get("SALARYCD（核薪方式）"))
        monthly_min = salary_to_monthly(salary_min, period)
        monthly_max = salary_to_monthly(salary_max, period)
        skills = extract_skills(title, description)
        source_url = clean_text(record.get("URL_QUERY（職缺資料URL）"))
        rows.append(
            {
                "job_id": stable_job_id("taiwanjobs", source_url or title, record.get("COMPNAME（公司名稱）")),
                "title": title,
                "company": clean_text(record.get("COMPNAME（公司名稱）")),
                "description": description,
                "city": city,
                "district": district,
                "country": "Taiwan",
                "location": location,
                "remote_type": infer_remote_type(description),
                "experience": clean_text(record.get("EXPERIENCE（工作經驗）")),
                "seniority": infer_seniority(record.get("EXPERIENCE（工作經驗）"), title, description),
                "job_type": clean_text(record.get("WK_TYPE（職務性質）")),
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_period": period,
                "salary_monthly_min": monthly_min,
                "salary_monthly_max": monthly_max,
                "education": clean_text(record.get("EDGRDESC（最低學歷要求）")),
                "source_platform": "TaiwanJobs",
                "source_url": source_url,
                "source_updated_at": format_yyyymmdd(record.get("TRANDATE（職缺更新日期）")) or source_updated_at,
                "fetched_at": fetched_at,
                "skills": skills,
                "career_cluster": classify_cluster(title, description, skills),
            }
        )
    return standardize_dataframe(pd.DataFrame(rows))


def normalize_cake_jobs(records: list[dict[str, Any]], *, fetched_at: str) -> pd.DataFrame:
    rows = []
    for entry in records:
        if isinstance(entry, tuple):
            path, record = entry
            salary = record.get("salary") or {}
            period = normalize_cake_salary_period(salary.get("type"))
            salary_min = parse_number(salary.get("min"))
            salary_max = parse_number(salary.get("max"))
            title = clean_text(record.get("title"))
            description = clean_text(record.get("description"))
            company = clean_text((record.get("page") or {}).get("name"))
            locations = record.get("locationsWithLocale") or record.get("locations") or []
            location = cake_location_to_text(locations)
            tags = record.get("tags") or []
            seniority = normalize_cake_seniority(record.get("seniorityLevel"))
            job_type = normalize_cake_job_type(record.get("jobType"))
            experience = str(record.get("minWorkExpYear", ""))
            updated_at = record.get("contentUpdatedAt")
        else:
            record = entry
            path = clean_text(record.get("path"))
            currency = clean_text(record.get("salary_currency") or record.get("searchable_salary_currency"))
            period = normalize_cake_salary_period(record.get("salary_type"))
            salary_min = parse_number(record.get("salary_min") or record.get("searchable_salary_min")) if currency in ("", "TWD") else None
            salary_max = parse_number(record.get("salary_max") or record.get("searchable_salary_max")) if currency in ("", "TWD") else None
            title = clean_text(record.get("title"))
            description = clean_text(record.get("description_plain_text") or record.get("description"))
            company = clean_text((record.get("page") or {}).get("name"))
            location = cake_location_to_text(
                record.get("flat_location_list")
                or record.get("flat_location_list_with_locale")
                or record.get("location_list")
                or record.get("locationsWithLocale")
                or record.get("locations")
                or []
            )
            tags = record.get("tag_list") or record.get("tags") or []
            seniority = normalize_cake_seniority(record.get("seniority_level") or record.get("seniorityLevel"))
            job_type = normalize_cake_job_type(record.get("job_type") or record.get("jobType"))
            experience = str(record.get("min_work_exp_year") or record.get("minWorkExpYear") or "")
            updated_at = record.get("content_updated_at") or record.get("contentUpdatedAt")
        city, district = split_taiwan_location(location)
        skills = extract_skills(title, description, " ".join(clean_text(tag) for tag in tags))
        url = f"https://www.cake.me/jobs/{path}"
        rows.append(
            {
                "job_id": stable_job_id("cake", path),
                "title": title,
                "company": company,
                "description": description,
                "city": city,
                "district": district,
                "country": "Taiwan",
                "location": location,
                "remote_type": infer_remote_type(description),
                "experience": experience,
                "seniority": seniority,
                "job_type": job_type,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_period": period,
                "salary_monthly_min": salary_to_monthly(salary_min, period),
                "salary_monthly_max": salary_to_monthly(salary_max, period),
                "education": "",
                "source_platform": "Cake",
                "source_url": url,
                "source_updated_at": updated_at,
                "fetched_at": fetched_at,
                "skills": skills,
                "career_cluster": classify_cluster(title, description, skills),
            }
        )
    return standardize_dataframe(pd.DataFrame(rows))


def normalize_meetjobs(records: list[dict[str, Any]], *, fetched_at: str) -> pd.DataFrame:
    rows = []
    for record in records:
        salary_min, salary_max, period = parse_meetjobs_salary(record.get("salary", ""))
        if isinstance(record.get("salary"), dict):
            salary_min, salary_max, period = parse_meetjobs_api_salary(record.get("salary"))
        title = clean_text(record.get("title"))
        employer = record.get("employer") or {}
        company = clean_text(record.get("company") or employer.get("name") or record.get("external_employer_name"))
        tags = record.get("tags") or [item.get("name", "") for item in (record.get("required_skills") or []) if isinstance(item, dict)]
        description = clean_text(strip_html(record.get("description"))) or " ".join(tags)
        address = clean_text(record.get("address"))
        source_url = record.get("url") or meetjobs_url(record)
        skills = extract_skills(title, company, description, " ".join(clean_text(tag) for tag in tags))
        cluster = classify_cluster(title, description, skills)
        if not is_cs_it_job(title, description, skills, cluster):
            continue
        rows.append(
            {
                "job_id": stable_job_id("meetjobs", source_url, title, company),
                "title": title,
                "company": company,
                "description": description,
                "city": infer_city_from_text(f"{address} {title}"),
                "district": "",
                "country": "Taiwan",
                "location": address or infer_city_from_text(title) or "Taiwan",
                "remote_type": infer_remote_type(title, description),
                "experience": "",
                "seniority": infer_seniority("", title, description),
                "job_type": clean_text(record.get("work_type") or record.get("contract_type")),
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_period": period,
                "salary_monthly_min": salary_to_monthly(salary_min, period),
                "salary_monthly_max": salary_to_monthly(salary_max, period),
                "education": "",
                "source_platform": "Meet.jobs",
                "source_url": source_url,
                "source_updated_at": clean_text(record.get("updated_at") or record.get("published_at")),
                "fetched_at": fetched_at,
                "skills": skills,
                "career_cluster": cluster,
            }
        )
    return standardize_dataframe(pd.DataFrame(rows))


def normalize_one1111(records: list[dict[str, Any]], *, fetched_at: str) -> pd.DataFrame:
    rows = []
    for record in records:
        title = clean_text(record.get("title"))
        snippet = clean_text(record.get("snippet"))
        source_url = clean_text(record.get("url"))
        skills = extract_skills(title, snippet)
        cluster = classify_cluster(title, snippet, skills)
        if not is_cs_it_job(title, snippet, skills, cluster):
            continue
        salary_min, salary_max, period = parse_one1111_salary(snippet)
        city, district = split_taiwan_location(snippet)
        rows.append(
            {
                "job_id": stable_job_id("1111", source_url, title),
                "title": title,
                "company": infer_one1111_company(snippet, title),
                "description": snippet,
                "city": city,
                "district": district,
                "country": "Taiwan",
                "location": city or "Taiwan",
                "remote_type": infer_remote_type(title, snippet),
                "experience": infer_one1111_experience(snippet),
                "seniority": infer_seniority(snippet, title, snippet),
                "job_type": infer_one1111_job_type(snippet),
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_period": period,
                "salary_monthly_min": salary_to_monthly(salary_min, period),
                "salary_monthly_max": salary_to_monthly(salary_max, period),
                "education": infer_one1111_education(snippet),
                "source_platform": "1111",
                "source_url": source_url,
                "source_updated_at": "",
                "fetched_at": fetched_at,
                "skills": skills,
                "career_cluster": cluster,
            }
        )
    return standardize_dataframe(pd.DataFrame(rows))


def standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for column in STANDARD_COLUMNS:
        if column not in df.columns:
            df[column] = None
    df = df[STANDARD_COLUMNS].copy()
    df = df[df["title"].fillna("").str.strip().ne("")]
    df["skills"] = df["skills"].apply(lambda value: value if isinstance(value, list) else [])
    numeric_columns = [
        "salary_min",
        "salary_max",
        "salary_monthly_min",
        "salary_monthly_max",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    text_columns = [column for column in STANDARD_COLUMNS if column not in numeric_columns and column != "skills"]
    for column in text_columns:
        df[column] = df[column].apply(clean_text)
    return df.drop_duplicates(subset=["job_id"])


def clean_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def stable_job_id(*parts: Any) -> str:
    import hashlib

    raw = "|".join(clean_text(part) for part in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def parse_number(value: Any) -> float | None:
    text = clean_text(value).replace(",", "")
    if not text or text == "-":
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", text, flags=re.I)
    if not match:
        return None
    number = float(match.group(1))
    if re.search(r"(?<=\d)\s*k\b|\bk\b", text, flags=re.I):
        number *= 1000
    if re.search(r"(?<=\d)\s*m\b|\bm\b", text, flags=re.I):
        number *= 1_000_000
    return number


def normalize_salary_period(value: Any) -> str:
    text = clean_text(value).lower()
    if "時薪" in text or "hour" in text:
        return "hour"
    if "年薪" in text or "annual" in text or "year" in text:
        return "year"
    if "日薪" in text or "daily" in text or "day" in text:
        return "day"
    if "論件" in text or "piece" in text:
        return "piece"
    return "month"


def normalize_cake_salary_period(value: Any) -> str:
    text = clean_text(value)
    return {
        "per_hour": "hour",
        "per_year": "year",
        "per_day": "day",
        "per_month": "month",
    }.get(text, normalize_salary_period(text))


def salary_to_monthly(value: float | None, period: str) -> float | None:
    if value is None:
        return None
    if period == "year":
        return round(value / 12, 2)
    if period == "day":
        return round(value * 22, 2)
    if period == "hour":
        return round(value * 8 * 22, 2)
    if period == "piece":
        return None
    return value


def parse_meetjobs_salary(value: Any) -> tuple[float | None, float | None, str]:
    text = clean_text(value)
    period = normalize_salary_period(text)
    numbers = [parse_number(match) for match in re.findall(r"\d+(?:\.\d+)?\s*[kmKM]?", text)]
    numbers = [number for number in numbers if number is not None]
    if not numbers:
        return None, None, period
    if "+" in text or len(numbers) == 1:
        return numbers[0], None, period
    return numbers[0], numbers[1], period


def parse_meetjobs_api_salary(value: dict[str, Any]) -> tuple[float | None, float | None, str]:
    period = {
        "monthly": "month",
        "yearly": "year",
        "annually": "year",
        "hourly": "hour",
        "daily": "day",
    }.get(clean_text(value.get("paid_period_key")).lower(), normalize_salary_period(value.get("paid_period")))
    return parse_number(value.get("minimum")), parse_number(value.get("maximum")), period


def parse_one1111_salary(value: Any) -> tuple[float | None, float | None, str]:
    text = clean_text(value)
    period = normalize_salary_period(text)
    salary_match = re.search(r"(月薪|年薪|時薪|日薪|面議)[^\d]*(\d[\d,]*)?\s*(?:~|至|-)?\s*(\d[\d,]*)?", text)
    if not salary_match:
        return None, None, period
    if "面議" in salary_match.group(1):
        return None, None, period
    salary_min = parse_number(salary_match.group(2))
    salary_max = parse_number(salary_match.group(3))
    return salary_min, salary_max, period


def infer_one1111_company(snippet: str, title: str) -> str:
    text = snippet.replace(title, "", 1).strip()
    parts = re.split(r"\s{2,}|｜|\|", text)
    for part in parts:
        part = clean_text(part)
        if part and not any(token in part for token in ("月薪", "年薪", "時薪", "日薪", "面議", "工作內容")):
            return part[:80]
    return ""


def infer_one1111_experience(snippet: str) -> str:
    match = re.search(r"(\d+\s*年以上|不拘|無經驗可|經驗不拘)", snippet)
    return match.group(1).replace(" ", "") if match else ""


def infer_one1111_education(snippet: str) -> str:
    match = re.search(r"(高中職|專科|大學|碩士|博士)以上?", snippet)
    return match.group(0) if match else ""


def infer_one1111_job_type(snippet: str) -> str:
    for token in ("全職", "兼職", "工讀", "實習", "派遣", "約聘"):
        if token in snippet:
            return token
    return ""


def strip_html(value: Any) -> str:
    return re.sub(r"<[^>]+>", " ", clean_text(value))


def meetjobs_url(record: dict[str, Any]) -> str:
    identifier = clean_text(record.get("id"))
    slug = clean_text(record.get("slug"))
    if identifier and slug:
        return f"https://meet.jobs/en/jobs/{identifier}-{slug}"
    if identifier:
        return f"https://meet.jobs/en/jobs/{identifier}"
    return ""


def is_cs_it_job(title: Any, description: Any, skills: list[str], cluster: str) -> bool:
    if cluster != "Other CS" or skills:
        return True
    text = f"{title or ''} {description or ''}".lower()
    keywords = (
        "software",
        "developer",
        "engineer",
        "programmer",
        "frontend",
        "front-end",
        "backend",
        "back-end",
        "full stack",
        "full-stack",
        "devops",
        "sre",
        "data",
        "machine learning",
        "security",
        "cyber",
        "firmware",
        "embedded",
        "qa",
        "test",
        "mis",
        "it support",
        "軟體",
        "工程師",
        "程式",
        "前端",
        "後端",
        "全端",
        "資料",
        "雲端",
        "資安",
        "韌體",
        "嵌入式",
        "測試",
        "資訊",
        "系統",
        "網管",
    )
    return any(keyword in text for keyword in keywords)


def split_taiwan_location(location: str) -> tuple[str, str]:
    location = clean_text(location)
    city_match = re.search(r"(台北市|臺北市|新北市|桃園市|新竹市|新竹縣|台中市|臺中市|台南市|臺南市|高雄市|基隆市|宜蘭縣|苗栗縣|彰化縣|南投縣|雲林縣|嘉義市|嘉義縣|屏東縣|花蓮縣|台東縣|臺東縣|澎湖縣|金門縣|連江縣)", location)
    city = city_match.group(1).replace("臺", "台") if city_match else ""
    district = ""
    if city:
        tail = location.split(city_match.group(1), 1)[-1]
        district_match = re.search(r"([\u4e00-\u9fff]{1,4}(?:區|鄉|鎮|市))", tail)
        district = district_match.group(1) if district_match else ""
    return city, district


def infer_city_from_text(text: str) -> str:
    return split_taiwan_location(text)[0]


def infer_remote_type(*texts: Any) -> str:
    text = " ".join(clean_text(value).lower() for value in texts)
    if any(token in text for token in ("remote", "遠端", "在家工作", "work from home")):
        return "Remote"
    if any(token in text for token in ("hybrid", "混合", "部分遠端")):
        return "Hybrid"
    return "Onsite/Unspecified"


def infer_seniority(experience: Any, title: Any, description: Any = "") -> str:
    text = f"{experience or ''} {title or ''} {description or ''}".lower()
    if any(token in text for token in ("intern", "實習")):
        return "Internship"
    if any(token in text for token in ("senior", "資深", "lead", "principal", "architect", "3年以上", "5年以上")):
        return "Senior"
    if any(token in text for token in ("junior", "entry", "新鮮人", "無", "不拘", "1年內")):
        return "Entry"
    return "Mid/Unspecified"


def normalize_cake_seniority(value: Any) -> str:
    text = clean_text(value)
    return {
        "internship_level": "Internship",
        "entry_level": "Entry",
        "mid_senior_level": "Senior",
    }.get(text, "Mid/Unspecified")


def normalize_cake_job_type(value: Any) -> str:
    return clean_text(value).replace("_", " ").title()


def cake_location_to_text(locations: Any) -> str:
    if isinstance(locations, list):
        parts = []
        for item in locations:
            if isinstance(item, dict):
                parts.append(item.get("zh-TW") or item.get("zh-tw") or item.get("en") or "")
            else:
                parts.append(str(item))
        return "; ".join(part for part in parts if part)
    return clean_text(locations)


def format_yyyymmdd(value: Any) -> str:
    text = clean_text(value)
    if re.fullmatch(r"\d{8}", text):
        return datetime.strptime(text, "%Y%m%d").date().isoformat()
    return text
