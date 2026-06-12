from src.ingest.cake import extract_algolia_credentials, fetch_algolia_records, parse_next_data
from src.ingest.meetjobs import fetch_records
from src.ingest.one1111 import parse_records as parse_one1111_records
from src.ingest.taiwanjobs import parse_webservice_xml


def test_cake_next_data_credentials_and_algolia_pagination(monkeypatch):
    html = """
    <script id="__NEXT_DATA__" type="application/json">
    {"props":{"pageProps":{"initialState":{"auth":{"kickoff":{"algolia":{"id":"APP123","key_global_search":"KEY456"}}}}}}}
    </script>
    """
    next_data = parse_next_data(html)
    assert extract_algolia_credentials(next_data) == ("APP123", "KEY456")

    def fake_fetch_page(app_id, api_key, page):
        return {
            "results": [
                {
                    "nbPages": 5,
                    "hits": [{"path": f"job-{page}", "title": f"Job {page}"}],
                }
            ]
        }

    monkeypatch.setattr("src.ingest.cake.fetch_algolia_page", fake_fetch_page)
    records, pages = fetch_algolia_records("APP123", "KEY456", max_pages=2)

    assert [record["path"] for record in records] == ["job-0", "job-1"]
    assert len(pages) == 2


def test_meetjobs_api_pagination_contract(monkeypatch):
    pages = {
        1: {
            "collection": [
                {
                    "id": 1,
                    "slug": "software-engineer",
                    "title": "Software Engineer",
                }
            ],
            "paginator": {"total_pages": 2},
        },
        2: {
            "collection": [
                {
                    "id": 2,
                    "slug": "sre",
                    "title": "SRE",
                }
            ],
            "paginator": {"total_pages": 2},
        },
    }

    def fake_get_json(url, timeout=45, params=None, headers=None):
        return pages[params["page"]]

    monkeypatch.setattr("src.ingest.meetjobs.get_json", fake_get_json)
    records, raw_pages = fetch_records()

    assert [record["slug"] for record in records] == ["software-engineer", "sre"]
    assert len(raw_pages) == 2


def test_one1111_search_page_parsing_contract():
    html = """
    <html><body>
      <div class="job-item">
        <a href="/job/132004582?mid=searchlist">API 服務研發工程師 （土城）</a>
        <span>鴻海精密工業股份有限公司</span>
        <span>新北市土城區</span>
        <span>月薪 60,000 至 100,000</span>
        <p>熟悉 Node.js / Go / Python、Kubernetes、CI/CD。</p>
      </div>
    </body></html>
    """
    records = parse_one1111_records(html, keyword="API", page=1)

    assert len(records) == 1
    assert records[0]["title"] == "API 服務研發工程師 （土城）"
    assert records[0]["url"] == "https://www.1111.com.tw/job/132004582"
    assert records[0]["keyword"] == "API"


def test_taiwanjobs_webservice_xml_parser():
    xml = """
    <DataList>
      <Data>
        <OCCU_DESC（職務名稱）><![CDATA[軟體工程師]]></OCCU_DESC（職務名稱）>
        <CJOB1_COUNT（職務大類別代碼）><![CDATA[08]]></CJOB1_COUNT（職務大類別代碼）>
        <CITYNAME（工作地點）><![CDATA[新竹市新竹市]]></CITYNAME（工作地點）>
      </Data>
    </DataList>
    """
    records = parse_webservice_xml(xml)
    assert records == [
        {
            "OCCU_DESC（職務名稱）": "軟體工程師",
            "CJOB1_COUNT（職務大類別代碼）": "08",
            "CITYNAME（工作地點）": "新竹市新竹市",
        }
    ]
