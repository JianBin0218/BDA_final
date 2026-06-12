import pandas as pd

from src.ingest.cake import CakeSchemaWarning
from src.normalization import normalize_cake_jobs, normalize_meetjobs, normalize_one1111, normalize_taiwanjobs, parse_meetjobs_api_salary, parse_meetjobs_salary, parse_one1111_salary, split_taiwan_location
from src.skills import extract_skills


def test_taiwanjobs_normalization_filters_core_fields():
    records = [
        {
            "OCCU_DESC（職務名稱）": "後端工程師",
            "WK_TYPE（職務性質）": "全職",
            "JOB_DETAIL（工作內容）": "開發 RESTful API，熟悉 Python、SQL、Docker。",
            "CITYNAME（工作地點）": "台北市信義區",
            "EXPERIENCE（工作經驗）": "3年以上",
            "SALARYCD（核薪方式）": "月薪",
            "NT_L（薪資範圍下限）": "60000",
            "NT_U（薪資範圍上限）": "90000",
            "EDGRDESC（最低學歷要求）": "大學",
            "URL_QUERY（職缺資料URL）": "https://example.com/job/1",
            "COMPNAME（公司名稱）": "Example Co",
            "TRANDATE（職缺更新日期）": "20260611",
        }
    ]
    df = normalize_taiwanjobs(records, fetched_at="2026-06-11T00:00:00Z", source_updated_at="2026-06-11")

    assert len(df) == 1
    row = df.iloc[0]
    assert row["country"] == "Taiwan"
    assert row["city"] == "台北市"
    assert row["district"] == "信義區"
    assert row["salary_monthly_min"] == 60000
    assert row["source_updated_at"] == "2026-06-11"
    assert "Python" in row["skills"]
    assert row["career_cluster"] == "Cloud / DevOps / SRE"


def test_chinese_and_english_skill_extraction():
    skills = extract_skills("資安韌體前端後端資料庫雲端機器學習", "K8S Golang Vue React")
    for expected in ["Cybersecurity", "Firmware/Embedded", "Cloud", "Machine Learning", "Kubernetes", "Golang", "Vue", "React"]:
        assert expected in skills


def test_meetjobs_salary_parser_monthly_and_annual():
    assert parse_meetjobs_salary("58k - 77k TWD Monthly") == (58000.0, 77000.0, "month")
    assert parse_meetjobs_salary("1.6m+ TWD Annually") == (1600000.0, None, "year")
    assert parse_meetjobs_api_salary({"minimum": 95000, "maximum": None, "paid_period_key": "monthly"}) == (95000.0, None, "month")


def test_cake_algolia_hit_normalization():
    df = normalize_cake_jobs(
        [
            {
                "path": "senior-sre",
                "title": "Senior SRE engineer",
                "description_plain_text": "K8S, Linux, CI/CD",
                "page": {"name": "Example Tech"},
                "flat_location_list": ["松山區, 台北市, 台灣"],
                "salary_min": 1600000,
                "salary_max": 2200000,
                "salary_type": "per_year",
                "salary_currency": "TWD",
                "tag_list": ["K8S", "DevOps", "CI/CD"],
                "seniority_level": "mid_senior_level",
                "job_type": "full_time",
                "min_work_exp_year": 4,
                "content_updated_at": "2026-06-11T00:00:00Z",
            }
        ],
        fetched_at="2026-06-11T00:00:00Z",
    )

    row = df.iloc[0]
    assert row["source_platform"] == "Cake"
    assert row["company"] == "Example Tech"
    assert row["city"] == "台北市"
    assert row["salary_monthly_min"] == 133333.33
    assert row["career_cluster"] == "Cloud / DevOps / SRE"


def test_meetjobs_api_normalization_filters_non_cs_jobs():
    df = normalize_meetjobs(
        [
            {
                "id": 1,
                "slug": "software-engineer",
                "title": "Software Engineer 軟體工程師",
                "description": "<p>Build ASP.NET, Vue.js and Docker services.</p>",
                "employer": {"name": "TITANSOFT"},
                "salary": {"minimum": 95000, "maximum": None, "paid_period_key": "monthly"},
                "required_skills": [{"name": "C#"}, {"name": "Docker"}],
                "work_type": "Full Time",
                "updated_at": "2026-05-20T10:24:21.932+08:00",
            },
            {
                "id": 2,
                "slug": "career-consulting",
                "title": "Career Consulting Service",
                "description": "Coaching package",
                "employer": {"name": "Meet.jobs"},
            },
        ],
        fetched_at="2026-06-11T00:00:00Z",
    )

    assert len(df) == 1
    row = df.iloc[0]
    assert row["source_url"] == "https://meet.jobs/en/jobs/1-software-engineer"
    assert row["salary_monthly_min"] == 95000
    assert "Docker" in row["skills"]


def test_one1111_normalization_filters_and_salary():
    assert parse_one1111_salary("月薪 60,000 至 100,000 元") == (60000.0, 100000.0, "month")
    df = normalize_one1111(
        [
            {
                "title": "API 服務研發工程師 （土城）",
                "url": "https://www.1111.com.tw/job/132004582",
                "snippet": "API 服務研發工程師 （土城） 鴻海精密工業股份有限公司 新北市土城區 月薪 60,000 至 100,000 熟悉 Node.js Python Kubernetes CI/CD",
            },
            {
                "title": "行政助理",
                "url": "https://www.1111.com.tw/job/1",
                "snippet": "行政庶務 接待訪客 文件整理",
            },
        ],
        fetched_at="2026-06-11T00:00:00Z",
    )

    assert len(df) == 1
    row = df.iloc[0]
    assert row["source_platform"] == "1111"
    assert row["city"] == "新北市"
    assert row["district"] == "土城區"
    assert row["salary_monthly_max"] == 100000
    assert "Python" in row["skills"]


def test_split_taiwan_location():
    assert split_taiwan_location("新北市板橋區") == ("新北市", "板橋區")


def test_cake_schema_warning_is_non_fatal_type():
    assert issubclass(CakeSchemaWarning, RuntimeError)
