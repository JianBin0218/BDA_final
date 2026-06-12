from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_DIR = DATA_DIR / "db"

TAIWANJOBS_DATASET_URL = "https://apiservice.mol.gov.tw/OdService/rest/dataset/44062"
TAIWANJOBS_JSON_URL = "https://apiservice.mol.gov.tw/OdService/download/A17000000J-030144-nkP"
TAIWANJOBS_WEBSERVICE_URL = "https://free.taiwanjobs.gov.tw/webservice_taipei/Webservice.ashx"
CAKE_TAIWAN_IT_URL = "https://www.cake.me/jobs/for-it/in-Taiwan?locale=en"
CAKE_ALGOLIA_MAX_PAGES = 250
MEETJOBS_TAIWAN_API_URL = "https://api.meet.jobs/api/v1/jobs"
ONE1111_SEARCH_URL = "https://www.1111.com.tw/search/job"
ONE1111_KEYWORDS = [
    "軟體工程師",
    "前端工程師",
    "後端工程師",
    "資料工程師",
    "AI工程師",
    "DevOps",
    "SRE",
    "資安",
    "韌體工程師",
    "嵌入式工程師",
    "QA工程師",
    "MIS",
    "系統工程師",
    "網管",
    "API",
    "Python",
    "JavaScript",
]
ONE1111_MAX_PAGES_PER_KEYWORD = 3


def ensure_data_dirs() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, DB_DIR):
        path.mkdir(parents=True, exist_ok=True)
