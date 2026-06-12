# SkillScope

## A Big Data System for Market-Wide CS Career Intelligence

**完整企畫書 / Project Proposal**

---

> **Project Goal**  
> 將公開 CS 職缺資料轉換成可變現的職涯情報產品：使用者可以理解整體 CS job market、比較不同 career clusters、找出自身 skill gap，並獲得對應的學習資源建議。

## Project Metadata

| Item | Description |
|---|---|
| Course | Big Data Systems Final Project |
| Product Name | SkillScope |
| Primary Users | CS students and career changers |
| Potential Paying Customers | University career centers, bootcamps, online learning platforms |
| Core Deliverable | Dashboard + personalized skill-gap report generator + learning resource recommendation |
| Deployment Target | Streamlit Cloud / Render / Hugging Face Spaces |

**Note:** LLM-generated career advice paragraph is intentionally deferred until the full core system is completed.

---

# 1. Executive Summary

SkillScope 是一個 market-wide CS career intelligence platform。它收集公開 CS 相關職缺，從 job descriptions 中抽取技能需求，將大量職缺分類或分群成 career clusters，並透過 dashboard 與 personalized skill-gap report 幫助 CS 學生、研究生與轉職者做職涯決策。

本專題的核心不是建立另一個 job board，而是將分散、非結構化的職缺文字資料轉換成可行動的職涯情報。使用者不只可以看到哪些技能熱門，也可以知道自己的技能最接近哪個職涯方向、若想轉往某個 career cluster 還缺哪些高需求技能，以及該優先學習哪些資源。

此系統符合 Big Data Systems final project 的精神：資料本身不直接產生價值，價值來自將 raw data refined into a product that someone is willing to pay for。SkillScope 的 monetization model 以學生個人報告、career center dashboard、bootcamp/course platform insight report 為主。

> **One-Sentence Product Definition**  
> SkillScope transforms public CS job postings into a market-wide career map and personalized skill-gap reports for CS students, career changers, and university career centers.

---

# 2. Product Motivation and Problem Statement

CS 學生與轉職者面臨的問題不是缺少職缺資訊，而是資訊過度分散、缺乏結構化理解。一般 job boards 讓使用者搜尋職缺，但很少回答以下問題：

- 整體 CS job market 目前有哪些主要 career clusters？
- 不同 career clusters 分別需要哪些核心技能？
- 哪些技能是跨領域高價值技能？
- 對 junior 或轉職者而言，哪些方向比較適合作為 entry point？
- 如果我目前會 Python、SQL、React，我最接近哪類職涯？
- 若我想成為 Cloud Engineer 或 ML Engineer，我應該先補什麼技能？

SkillScope 的價值在於把大量職缺資料轉換成 career decision intelligence。它將 job title、job description、salary、location、remote type、seniority 等資料整合後，提供 dashboard、career cluster analysis、skill overlap analysis 與 personalized skill-gap report。

---

# 3. Target Customers

SkillScope 採用 two-sided customer design：學生與轉職者是主要使用者，學校 career centers、bootcamps 與線上課程平台則是潛在付費客戶。

| Customer Segment | Pain Point | Potential Product / Pricing |
|---|---|---|
| CS Students / Graduate Students | 不知道該走 frontend、backend、data、AI、cloud、security 等哪條路線。 | 免費 dashboard + 低價個人化報告 |
| Career Changers | 缺乏對 CS 市場結構與技能門檻的理解，需要知道最短補強路線。 | 個人 skill-gap report / subscription |
| University Career Centers | 需要掌握產業需求，協助學生選課、就業輔導與課程調整。 | institution dashboard / semester report |
| Bootcamps / Online Course Platforms | 需要了解市場技能需求，設計課程、導流課程與定位廣告。 | market insight API / skill-demand reports |

---

# 4. Value Proposition

| Value Layer | Description |
|---|---|
| From raw postings to career map | 把雜亂的 job postings 整理成 market-wide CS career clusters。 |
| From skill keywords to decision support | 不只列出熱門技能，也計算技能重疊、career fit score 與 skill gap。 |
| From dashboard to action | 將 missing skills 連接到 learning resources，讓使用者知道下一步要學什麼。 |
| From student use to institutional value | 學生能做個人職涯決策，學校與課程平台能做 curriculum alignment 與 market analysis。 |

---

# 5. Required System Scope

本企畫將原本 optional 的 search/filtering、course recommendation、trend over time 與 live deployment 納入必做範圍。LLM-generated career advice paragraph 暫時不納入 core scope，待完整版本完成後再決定是否加入。

| # | Module | Description |
|---:|---|---|
| 1 | Public CS job posting collection | 收集公開 CS 相關職缺資料，涵蓋 software、data、AI、cloud、security、mobile、QA、systems 等方向。 |
| 2 | Cleaning and preprocessing | 清理 HTML/noisy text、去重、標準化職稱/地點、解析 salary、remote type、seniority。 |
| 3 | Skill extraction | 從 job descriptions 抽取 programming languages、frameworks、data tools、cloud/DevOps、AI/ML、安全等技能。 |
| 4 | Career cluster classification / clustering | 結合 rule-based role classification 與 skill-based clustering，建立 market-wide CS career map。 |
| 5 | Dashboard | 顯示 cluster distribution、top skills、skill overlap、salary/location/remote analysis、search/filtering、trend over time。 |
| 6 | Personalized skill-gap report | 使用者輸入 current skills 與 target cluster，輸出 career fit score、matched/missing skills、learning priorities。 |
| 7 | Course / learning resource recommendation | 將 missing high-demand skills 對應到課程或官方學習資源。 |
| 8 | Live deployment | 部署互動式 dashboard 與 report generator，提供可開啟的 demo URL。 |

---

# 6. Demand Evidence Plan

由於本專案不打算使用訪談或問卷，需求證據將完全來自公開資料。報告中必須清楚記錄 data acquisition process，證明需求不是主觀猜測，而是從可觀察資料中推導出來。

| Evidence Type | How to Collect | Why It Supports Demand |
|---|---|---|
| Job posting volume | 收集大量 CS 相關職缺，統計不同職涯方向的職缺量。 | 證明市場規模與需求存在。 |
| Skill frequency | 統計技能在 job descriptions 中的出現頻率。 | 證明學生需要知道哪些技能值得優先學。 |
| Salary / remote / location patterns | 若資料可得，分析薪資區間、地點與遠端比例。 | 證明資訊可轉化為決策價值。 |
| Competitor / analogous products | 比較 job boards、career platforms、course platforms、resume tools 的定位與收費模式。 | 證明 career intelligence 類產品存在 willingness to pay。 |
| Course-platform alignment | 分析缺口技能能否對應到課程或學習資源。 | 證明 bootcamp/online course platforms 有潛在 B2B 價值。 |

---

# 7. System Architecture

系統採用 ingestion -> storage -> processing -> analytics -> delivery 的資料管線。初版可以使用 Python scripts + DuckDB/SQLite + Streamlit 完成，未來可擴展到 message queue、distributed processing 與 cloud storage。

| Layer | Design |
|---|---|
| Public Job Sources | Kaggle datasets, public job boards, company career pages, ATS pages, manually downloaded public datasets |
| Data Ingestion | Dataset loader, API collector, crawler, scheduled data refresh script |
| Raw Storage | CSV / JSON / Parquet files as raw immutable data |
| Processing Layer | Cleaning, deduplication, salary parsing, remote detection, skill extraction, seniority detection |
| Career Intelligence Layer | Role classification, skill vectorization, clustering, trend calculation, skill overlap analysis |
| Analytical Database | DuckDB or SQLite for local analytics; PostgreSQL for scalable version |
| Delivery Layer | Streamlit dashboard, filters, personalized report generator, course recommendation module |

## 7.1 Architecture Diagram

```text
Public Job Sources
Kaggle datasets / public job boards / company career pages
        ↓
Data Ingestion
Dataset loaders, API collectors, crawlers, scheduled refresh scripts
        ↓
Raw Storage
Raw CSV, JSON, or Parquet files kept as immutable source data
        ↓
Processing Layer
Cleaning, deduplication, parsing, skill extraction, seniority detection
        ↓
Career Intelligence Layer
Role classification, skill clustering, overlap analysis, trend analysis
        ↓
Analytical Database
DuckDB / SQLite / PostgreSQL tables for dashboard queries
        ↓
Delivery Layer
Dashboard, filters, personalized report generator, learning resource recommendation
```

---

# 8. Data Model

系統資料表建議分成 job_postings、skills、job_skills、career_clusters、courses、reports。這樣可支援 dashboard、skill overlap、career fit scoring 與 course recommendation。

| Table | Key Fields |
|---|---|
| job_postings | job_id, title, company, location, remote_type, salary_min, salary_max, posted_date, description, source |
| skills | skill_id, skill_name, skill_category, canonical_name |
| job_skills | job_id, skill_id, extraction_method, confidence |
| career_clusters | cluster_id, cluster_name, role_keywords, top_skills, description |
| courses | course_id, skill_id, title, provider, url, level, price_type |
| reports | report_id, user_input_skills, target_cluster, fit_score, missing_skills, recommended_courses |

---

# 9. Feature Design

## 9.1 Dashboard

- Career cluster distribution: 顯示各類 CS 職涯方向的職缺數量與比例。
- Top skills by cluster: 顯示每個 cluster 的核心技能需求。
- Skill overlap analysis: 顯示技能在不同 clusters 間的共用程度，找出 transferable skills。
- Salary / location / remote analysis: 根據資料可用性顯示薪資分布、地點分布與 remote/hybrid/onsite 比例。
- Search and filtering: 支援依 cluster、skill、location、remote type、seniority、company 篩選。
- Trend over time: 若資料有 posted_date，分析技能需求、職缺類別與 remote ratio 的時間變化。

## 9.2 Personalized Skill-Gap Report Generator

Report Generator 是最具 monetization potential 的功能。使用者輸入 current skills，選擇 target career cluster，系統根據市場資料產生個人化分析。

| Component | Description |
|---|---|
| Input | Current skills, target career cluster, optional experience level |
| Fit Score | 計算使用者技能與目標 cluster top demanded skills 的重疊程度。 |
| Matched Skills | 列出使用者已具備且市場需求高的技能。 |
| Missing Skills | 列出目標職涯中高需求但使用者尚未具備的技能。 |
| Learning Priority | 依 skill demand、cluster importance、使用者缺口排序學習優先級。 |
| Alternative Clusters | 推薦相近但 fit score 更高的其他 career clusters。 |

## 9.3 Course / Learning Resource Recommendation

Course recommendation 採用 skill-to-resource mapping，而不是複雜推薦系統。每個 missing skill 對應到官方文件、免費課程、線上課程或開源教程。

| Missing Skill | Recommended Resource Type |
|---|---|
| PyTorch | PyTorch official tutorials, ML course modules |
| Docker | Docker official guide, containerization course |
| Kubernetes | Kubernetes basics, cloud-native deployment tutorials |
| SQL | SQL for data analysis resources |
| React | React official tutorial, frontend development courses |
| Spark / Kafka / Airflow | Big data engineering courses and official documentation |

---

# 10. Business Model and Monetization

| Plan | Features | Pricing Logic |
|---|---|---|
| Free Tier | Basic dashboard, top skills, cluster overview | Attract users and validate demand |
| Student Premium | Personalized skill-gap reports, learning priorities, saved reports | US$5-10 / month or per-report pricing |
| Career Center Plan | Aggregated dashboard, curriculum alignment, semester reports | US$500-2000 / semester |
| Bootcamp / Course Platform Plan | Skill-demand insights, course gap analysis, API/data feed | B2B subscription or report-based pricing |

主要 monetization hypothesis 是：個人使用者願意為個人化技能缺口報告付低額費用，而 institutions 願意為市場技能趨勢與 curriculum alignment 報告付較高費用。

---

# 11. Go-to-Market Difficulties and Risks

| Risk | Description | Mitigation |
|---|---|---|
| Trust | 使用者可能質疑職缺資料是否完整或過時。 | 清楚標示資料來源、更新時間、樣本數與分析限制。 |
| Data acquisition | 部分 job boards 可能限制 scraping 或資料欄位不完整。 | 優先使用公開資料集、公開 API、允許存取的 job pages，遵守 ToS 與 robots.txt。 |
| Coverage bias | 資料來源可能偏向遠端職缺、特定國家或科技公司。 | 在 dashboard 中揭露來源分布，避免宣稱代表全球完整市場。 |
| Cold start | 初期資料量不足時，trend over time 可能不穩定。 | 先以 snapshot analysis 做 core demo，之後定期收集建立 longitudinal data。 |
| Competition | LinkedIn、Glassdoor、Levels.fyi、course platforms 都有部分相關資訊。 | 差異化在 market-wide career map + skill gap + learning resource mapping。 |
| Legal / Privacy | 職缺內容可能有著作權或平台條款限制。 | 儲存必要欄位與 metadata，避免大量複製受保護內容，並保留來源引用。 |

---

# 12. Implementation Plan

建議實作採用 Python-first data stack，以降低部署與維護成本。初版強調可重現、可展示、資料流完整，而不是追求大型分散式系統。

| Layer | Candidate Tools |
|---|---|
| Data ingestion | Python, requests, pandas, dataset loaders, optional crawler |
| Storage | CSV/JSON raw files, Parquet processed files |
| Database | DuckDB or SQLite for prototype; PostgreSQL for scalable version |
| NLP / Skill extraction | Keyword dictionary + regex + normalization; optional embedding-based matching |
| Clustering | Skill vectorization + KMeans/HDBSCAN or rule-based + clustering hybrid |
| Dashboard | Streamlit, Plotly/Altair, Pandas/DuckDB queries |
| Deployment | Streamlit Cloud, Render, Hugging Face Spaces |
| Repository | GitHub with README, scripts, sample data, reproducible pipeline |

## 12.1 Milestones

| Milestone | Task | Output |
|---|---|---|
| Milestone 1 | Finalize data sources and collect initial job postings | Raw dataset + data source documentation |
| Milestone 2 | Build cleaning and skill extraction pipeline | Processed dataset + skill tables |
| Milestone 3 | Implement career classification / clustering | Career cluster labels + validation examples |
| Milestone 4 | Build dashboard with filters and core charts | Interactive dashboard demo |
| Milestone 5 | Build skill-gap report and course recommendation | Personalized report generator |
| Milestone 6 | Deploy and prepare final report | Live URL + GitHub README + PDF report |

---

# 13. Final Report Structure

建議最終英文報告採用以下章節。這個結構直接對應 final project rubric：target customer、demand evidence、system design、implementation、business model 與 go-to-market difficulties。

1. Introduction
2. Target Customers and Value Proposition
3. Evidence of Demand and Willingness to Pay
4. Product Overview
5. Data Sources and Data Acquisition Process
6. System Architecture
7. Data Processing and Skill Extraction
8. Career Clustering Method
9. Dashboard Design
10. Personalized Skill-Gap Report Generator
11. Course Recommendation Module
12. Business Model and Monetization
13. Go-to-Market Difficulties
14. Scalability, Cost, and Limitations
15. Implementation, Deployment, and GitHub Repository
16. Conclusion

---

# 14. Alignment with Grading Rubric

| Rubric Item | How SkillScope Addresses It | Weight |
|---|---|---|
| Target customer clarity | Primary: CS students and career changers. Paying: university career centers and bootcamps. | 20% |
| Demand evidence | Use public job postings, skill frequency, competitor pricing, and learning-resource demand instead of interviews. | 25% |
| Technical system design | End-to-end pipeline from ingestion to processing, clustering, dashboard, report generator, and deployment. | 40% |
| Writing and presentation | Clear architecture diagram, tables, dashboard screenshots, and report structure. | 15% |
| Bonus: GTM difficulties | Dedicated risk section covering data acquisition, trust, competition, legal issues, and unit economics. | +10% |
| Bonus: deployment | Streamlit/Render/Hugging Face Spaces live demo. | +10% |

---

# 15. Deferred Feature: LLM-Generated Career Advice Paragraph

LLM-generated career advice paragraph 暫時不納入 core system scope。原因是它屬於自然語言包裝層，而不是 Big Data pipeline 的核心。待 dashboard、skill-gap report、course recommendation 與 deployment 完成後，再決定是否加入。

若日後加入，建議將其定位為 enhancement：根據 already computed fit score、matched skills、missing skills 與 learning priorities，自動生成一段使用者友善的 career advice。為降低部署風險，也可以先使用 template-based generation，而非真正串接 LLM API。

---

# 16. Conclusion

SkillScope 的核心價值是把公開 CS job postings 轉換成可付費的 career intelligence product。它不只是顯示熱門技能，而是建立 market-wide CS career map，並讓學生與轉職者依照自身技能取得具體的 skill-gap report 與學習資源建議。

此企畫在技術面具備完整 data pipeline，在商業面具備明確 target customers 與 monetization model，在報告面也能清楚對應 final project 的 rubric。若能完成 live deployment，將同時具備系統展示、資料產品與加分項的優勢。

---

*SkillScope Project Proposal*
