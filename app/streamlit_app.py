from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PROCESSED_DIR
from src.pipeline.build_dataset import build_dataset


st.set_page_config(page_title="SkillScope 台灣 CS 職缺雷達", layout="wide")

COLORS = {
    "ink": "#17202A",
    "paper": "#F7F4EE",
    "panel": "#FFFFFF",
    "teal": "#087E8B",
    "coral": "#F25F5C",
    "gold": "#F5B841",
    "line": "#D9D3C7",
    "muted": "#68717A",
    "soft_teal": "#E5F3F4",
}

PLOT_COLORS = [COLORS["teal"], COLORS["coral"], COLORS["gold"], "#3A6EA5", "#6A994E", "#9D4EDD", "#E76F51"]

CLUSTER_ZH = {
    "Backend / Full-stack": "後端 / 全端",
    "Frontend": "前端",
    "Data / AI": "資料 / AI",
    "Cloud / DevOps / SRE": "雲端 / DevOps / SRE",
    "Cybersecurity": "資安",
    "Firmware / Embedded": "韌體 / 嵌入式",
    "QA / Test": "QA / 測試",
    "MIS / IT Support": "MIS / IT 支援",
    "Mobile": "行動應用",
    "Other CS": "其他科技職缺",
}

COLUMN_ZH = {
    "title": "職缺名稱",
    "company": "公司",
    "city": "城市",
    "salary_monthly_min": "月薪下限",
    "salary_monthly_max": "月薪上限",
    "seniority": "資歷",
    "career_cluster": "職涯群集",
    "skills": "技能",
    "source_platform": "資料來源",
    "source_url": "來源連結",
}


def apply_theme_css() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --ink: {COLORS["ink"]};
            --paper: {COLORS["paper"]};
            --panel: {COLORS["panel"]};
            --teal: {COLORS["teal"]};
            --coral: {COLORS["coral"]};
            --gold: {COLORS["gold"]};
            --line: {COLORS["line"]};
            --muted: {COLORS["muted"]};
        }}

        .stApp {{
            background:
                linear-gradient(90deg, rgba(8,126,139,0.08) 1px, transparent 1px),
                linear-gradient(180deg, rgba(8,126,139,0.06) 1px, transparent 1px),
                var(--paper);
            background-size: 36px 36px;
            color: var(--ink);
        }}

        .block-container {{
            max-width: 1320px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}

        [data-testid="stSidebar"] {{
            background: #0F1B24;
            border-right: 1px solid rgba(255,255,255,0.08);
        }}

        [data-testid="stSidebar"] * {{
            color: #F8F4EA;
        }}

        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
            background-color: rgba(8,126,139,0.28);
            border: 1px solid rgba(255,255,255,0.12);
        }}

        h1, h2, h3 {{
            color: var(--ink);
            letter-spacing: 0;
        }}

        h1 {{
            font-size: 2.45rem;
            line-height: 1.08;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }}

        h2, h3 {{
            font-weight: 760;
        }}

        .hero-wrap {{
            background: linear-gradient(135deg, #FFFFFF 0%, #F9F6EF 58%, #E8F4F5 100%);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 28px 30px 24px;
            box-shadow: 0 18px 40px rgba(23,32,42,0.08);
            position: relative;
            overflow: hidden;
        }}

        .hero-wrap:after {{
            content: "";
            position: absolute;
            right: -80px;
            top: -100px;
            width: 290px;
            height: 290px;
            border: 1px solid rgba(8,126,139,0.20);
            border-radius: 50%;
        }}

        .eyebrow {{
            display: inline-flex;
            gap: 8px;
            align-items: center;
            color: var(--teal);
            font-weight: 760;
            font-size: 0.86rem;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}

        .hero-copy {{
            max-width: 780px;
            color: #46515B;
            font-size: 1.02rem;
            line-height: 1.68;
            margin: 0.6rem 0 0;
        }}

        .source-note {{
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.55;
            border-left: 3px solid var(--gold);
            padding-left: 12px;
            margin-top: 18px;
        }}

        [data-testid="stMetric"] {{
            background: rgba(255,255,255,0.92);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px 18px;
            box-shadow: 0 8px 22px rgba(23,32,42,0.055);
        }}

        [data-testid="stMetricLabel"] {{
            color: var(--muted);
            font-size: 0.88rem;
        }}

        [data-testid="stMetricValue"] {{
            color: var(--ink);
            font-weight: 820;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            background: rgba(255,255,255,0.74);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 6px;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 6px;
            padding: 10px 16px;
            color: var(--muted);
            font-weight: 720;
        }}

        .stTabs [aria-selected="true"] {{
            background: var(--ink);
            color: #FFFFFF;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 10px 26px rgba(23,32,42,0.06);
        }}

        .report-panel {{
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 18px 20px;
            margin-top: 10px;
            box-shadow: 0 10px 26px rgba(23,32,42,0.06);
        }}

        .chip-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
        }}

        .skill-chip {{
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            padding: 4px 10px;
            border-radius: 999px;
            background: {COLORS["soft_teal"]};
            color: var(--teal);
            border: 1px solid rgba(8,126,139,0.20);
            font-size: 0.9rem;
            font-weight: 680;
        }}

        .missing-chip {{
            background: #FFF3DC;
            color: #8B5A00;
            border-color: rgba(245,184,65,0.40);
        }}

        .danger-chip {{
            background: #FEEDEC;
            color: #A83A37;
            border-color: rgba(242,95,92,0.35);
        }}

        .section-note {{
            color: var(--muted);
            font-size: 0.95rem;
            margin-bottom: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    path = PROCESSED_DIR / "all_taiwan_jobs.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    if "skills" in df.columns:
        df["skills"] = df["skills"].apply(normalize_skill_list)
    return df


def normalize_skill_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, np.ndarray):
        return [str(item) for item in value.tolist() if str(item)]
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    if pd.isna(value):
        return []
    return [str(value)] if str(value) else []


def zh_cluster_name(cluster: str) -> str:
    return CLUSTER_ZH.get(cluster, cluster or "未分類")


def format_salary(min_value, max_value) -> str:
    if pd.isna(min_value) and pd.isna(max_value):
        return "未揭露"
    if pd.notna(min_value) and pd.notna(max_value):
        return f"NT$ {min_value:,.0f} - {max_value:,.0f}"
    if pd.notna(min_value):
        return f"NT$ {min_value:,.0f}+"
    return f"最高 NT$ {max_value:,.0f}"


def explode_skills(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "skills" not in df:
        return pd.DataFrame(columns=["skill"])
    out = df[["job_id", "career_cluster", "skills"]].explode("skills")
    return out.rename(columns={"skills": "skill"}).dropna()


def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        colorway=PLOT_COLORS,
        font={"family": "Noto Sans TC, Source Sans Pro, Arial, sans-serif", "color": COLORS["ink"]},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.72)",
        margin={"l": 18, "r": 18, "t": 56, "b": 28},
        title={"font": {"size": 18, "color": COLORS["ink"]}},
        xaxis={"gridcolor": "#ECE7DE", "zerolinecolor": COLORS["line"]},
        yaxis={"gridcolor": "#ECE7DE", "zerolinecolor": COLORS["line"]},
        legend={"orientation": "h", "y": -0.18},
    )
    return fig


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown("## 篩選條件")
        st.caption("用城市、技能、來源與薪資快速縮小台灣科技職缺市場。")
        sources = st.multiselect(
            "資料來源",
            sorted(df["source_platform"].dropna().unique()),
            default=sorted(df["source_platform"].dropna().unique()),
        )
        cluster_options = sorted(df["career_cluster"].dropna().unique(), key=zh_cluster_name)
        clusters = st.multiselect(
            "職涯群集",
            cluster_options,
            default=cluster_options,
            format_func=zh_cluster_name,
        )
        cities = st.multiselect("城市", sorted(city for city in df["city"].dropna().unique() if city), default=[])
        skills_df = explode_skills(df)
        skills = st.multiselect("技能", sorted(skills_df["skill"].dropna().unique()), default=[])
        salary_min = st.slider("最低可比月薪", 0, 200000, 0, 5000, format="NT$ %d")

        st.markdown("---")
        st.markdown("### 資料說明")
        st.caption("資料來源包含勞動部台灣就業通、Cake、Meet.jobs 與 1111。")

    filtered = df[df["source_platform"].isin(sources) & df["career_cluster"].isin(clusters)].copy()
    if cities:
        filtered = filtered[filtered["city"].isin(cities)]
    if skills:
        filtered = filtered[filtered["skills"].apply(lambda values: bool(set(normalize_skill_list(values)) & set(skills)))]
    if salary_min:
        filtered = filtered[
            filtered["salary_monthly_max"].fillna(filtered["salary_monthly_min"]).fillna(0) >= salary_min
        ]
    return filtered


def render_hero(df: pd.DataFrame) -> None:
    latest = pd.to_datetime(df["source_updated_at"], errors="coerce").max()
    latest_text = latest.date().isoformat() if pd.notna(latest) else "尚未取得"
    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="eyebrow">SkillScope Taiwan Radar</div>
            <h1>台灣 CS 職缺市場總覽</h1>
            <p class="hero-copy">
                把台灣即時職缺整理成可行動的職涯情報：看見地區分布、技能需求、薪資樣貌，
                並把個人技能對照到目標職涯方向。
            </p>
            <div class="source-note">
                目前資料來源包含台灣就業通、Cake 與 Meet.jobs；最近資料更新日：{latest_text}。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(df: pd.DataFrame) -> None:
    latest = pd.to_datetime(df["source_updated_at"], errors="coerce").max()
    with_salary = df["salary_monthly_min"].notna().sum()
    cities = df[df["city"].ne("")]["city"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("台灣 IT/CS 職缺", f"{len(df):,}")
    col2.metric("涵蓋城市", f"{cities:,}")
    col3.metric("可解析薪資", f"{with_salary:,}")
    col4.metric("最近更新", latest.date().isoformat() if pd.notna(latest) else "未知")


def render_market_overview(df: pd.DataFrame) -> None:
    st.markdown('<p class="section-note">從職涯群集與資料來源看台灣科技職缺的整體輪廓。</p>', unsafe_allow_html=True)
    left, right = st.columns(2)

    cluster_counts = df["career_cluster"].map(zh_cluster_name).value_counts().reset_index()
    cluster_counts.columns = ["職涯群集", "職缺數"]
    fig_cluster = px.bar(
        cluster_counts,
        x="職缺數",
        y="職涯群集",
        orientation="h",
        title="職涯群集分布",
        color="職涯群集",
        color_discrete_sequence=PLOT_COLORS,
    )
    left.plotly_chart(style_chart(fig_cluster), width="stretch")

    source_counts = df["source_platform"].value_counts().reset_index()
    source_counts.columns = ["資料來源", "職缺數"]
    fig_source = px.pie(
        source_counts,
        names="資料來源",
        values="職缺數",
        title="資料來源占比",
        color_discrete_sequence=PLOT_COLORS,
        hole=0.45,
    )
    right.plotly_chart(style_chart(fig_source), width="stretch")


def render_skills(df: pd.DataFrame) -> None:
    st.markdown('<p class="section-note">技能統計保留市場慣用英文名稱，方便直接對照履歷與職缺描述。</p>', unsafe_allow_html=True)
    skill_rows = explode_skills(df)
    if skill_rows.empty:
        st.info("目前篩選結果沒有可解析技能。")
        return

    left, right = st.columns(2)
    skill_counts = skill_rows["skill"].value_counts().head(20).reset_index()
    skill_counts.columns = ["技能", "職缺數"]
    fig_skill = px.bar(
        skill_counts,
        x="職缺數",
        y="技能",
        orientation="h",
        title="台灣科技職缺熱門技能",
        color_discrete_sequence=[COLORS["teal"]],
    )
    left.plotly_chart(style_chart(fig_skill), width="stretch")

    cluster_skill = (
        skill_rows.assign(職涯群集=skill_rows["career_cluster"].map(zh_cluster_name))
        .groupby(["職涯群集", "skill"])
        .size()
        .reset_index(name="職缺數")
        .sort_values(["職涯群集", "職缺數"], ascending=[True, False])
        .groupby("職涯群集")
        .head(5)
    )
    fig_heat = px.density_heatmap(
        cluster_skill,
        x="skill",
        y="職涯群集",
        z="職缺數",
        title="各職涯群集的技能熱度",
        color_continuous_scale=[[0, "#F8EFE3"], [0.5, COLORS["gold"]], [1, COLORS["teal"]]],
    )
    right.plotly_chart(style_chart(fig_heat), width="stretch")


def render_salary_location(df: pd.DataFrame) -> None:
    st.markdown('<p class="section-note">薪資已轉成可比較月薪；年薪除以 12，時薪以 8 小時、22 個工作天估算。</p>', unsafe_allow_html=True)
    left, right = st.columns(2)

    city_counts = df[df["city"].ne("")]["city"].value_counts().head(12).reset_index()
    city_counts.columns = ["城市", "職缺數"]
    fig_city = px.bar(city_counts, x="城市", y="職缺數", title="城市分布", color="城市", color_discrete_sequence=PLOT_COLORS)
    left.plotly_chart(style_chart(fig_city), width="stretch")

    salary_df = df.dropna(subset=["salary_monthly_min"]).copy()
    if salary_df.empty:
        right.info("目前篩選結果沒有可解析薪資。")
        return
    salary_df["salary_mid"] = salary_df[["salary_monthly_min", "salary_monthly_max"]].mean(axis=1)
    fig_salary = px.histogram(
        salary_df,
        x="salary_mid",
        nbins=30,
        title="可比月薪分布",
        labels={"salary_mid": "可比月薪（TWD）", "count": "職缺數"},
        color_discrete_sequence=[COLORS["coral"]],
    )
    right.plotly_chart(style_chart(fig_salary), width="stretch")


def render_skill_gap(df: pd.DataFrame) -> None:
    st.markdown('<p class="section-note">選擇目標職涯與目前技能，系統會用台灣職缺資料計算適配度與優先補強技能。</p>', unsafe_allow_html=True)
    skill_rows = explode_skills(df)
    if skill_rows.empty:
        st.info("目前篩選結果沒有可解析技能，無法產生技能缺口報告。")
        return

    all_skills = sorted(skill_rows["skill"].dropna().unique())
    target = st.selectbox("目標職涯方向", sorted(df["career_cluster"].dropna().unique(), key=zh_cluster_name), format_func=zh_cluster_name)
    current_skills = st.multiselect("目前已具備技能", all_skills)
    target_jobs = df[df["career_cluster"].eq(target)]
    target_skill_counts = Counter(skill for skills in target_jobs["skills"] for skill in normalize_skill_list(skills))
    top_required = [skill for skill, _ in target_skill_counts.most_common(12)]

    matched = sorted(set(current_skills) & set(top_required))
    missing = [skill for skill in top_required if skill not in set(current_skills)]
    fit_score = round((len(matched) / max(len(top_required), 1)) * 100)

    st.markdown('<div class="report-panel">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("適配分數", f"{fit_score}%")
    c2.metric("已對上技能", len(matched))
    c3.metric("優先補強技能", len(missing))

    st.markdown("#### 已具備且符合市場需求")
    render_chip_row(matched, empty_text="尚未選到與此方向高度重疊的技能。", chip_class="skill-chip")

    st.markdown("#### 建議優先補強")
    render_chip_row(missing[:8], empty_text="你已覆蓋此方向的主要技能需求。", chip_class="skill-chip missing-chip")
    st.markdown("</div>", unsafe_allow_html=True)

    alternatives = []
    for cluster, group in df.groupby("career_cluster"):
        required = set(skill for skills in group["skills"] for skill in normalize_skill_list(skills))
        score = round((len(set(current_skills) & required) / max(len(required), 1)) * 100)
        alternatives.append({"職涯群集": zh_cluster_name(cluster), "適配分數": score})
    alt_df = pd.DataFrame(alternatives).sort_values("適配分數", ascending=False).head(5)
    fig_alt = px.bar(
        alt_df,
        x="職涯群集",
        y="適配分數",
        title="相近職涯方向",
        color="職涯群集",
        color_discrete_sequence=PLOT_COLORS,
    )
    st.plotly_chart(style_chart(fig_alt), width="stretch")


def render_chip_row(values: list[str], *, empty_text: str, chip_class: str) -> None:
    if not values:
        st.markdown(f'<span class="skill-chip danger-chip">{empty_text}</span>', unsafe_allow_html=True)
        return
    chips = "".join(f'<span class="{chip_class}">{value}</span>' for value in values)
    st.markdown(f'<div class="chip-row">{chips}</div>', unsafe_allow_html=True)


def render_table(df: pd.DataFrame) -> None:
    st.markdown('<p class="section-note">下方顯示目前篩選條件下的前 200 筆職缺，方便回到原始來源查證。</p>', unsafe_allow_html=True)
    columns = [
        "title",
        "company",
        "city",
        "salary_monthly_min",
        "salary_monthly_max",
        "seniority",
        "career_cluster",
        "skills",
        "source_platform",
        "source_url",
    ]
    table = df[columns].head(200).copy()
    table["career_cluster"] = table["career_cluster"].map(zh_cluster_name)
    table["skills"] = table["skills"].apply(lambda values: ", ".join(normalize_skill_list(values)))
    table = table.rename(columns=COLUMN_ZH)
    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        column_config={
            "來源連結": st.column_config.LinkColumn("來源連結", display_text="開啟職缺"),
            "月薪下限": st.column_config.NumberColumn("月薪下限", format="NT$ %d"),
            "月薪上限": st.column_config.NumberColumn("月薪上限", format="NT$ %d"),
        },
    )


apply_theme_css()

data = load_data()
if data.empty:
    st.warning("找不到已處理資料。請先執行 `python -m src.pipeline.build_dataset`。")
    if st.button("立即擷取台灣資料"):
        with st.spinner("正在建立台灣職缺資料集..."):
            data = build_dataset()
            st.cache_data.clear()
            st.rerun()
else:
    filtered_data = filter_data(data)
    render_hero(filtered_data if not filtered_data.empty else data)
    st.write("")
    if filtered_data.empty:
        st.info("目前篩選條件沒有符合的職缺，請放寬城市、技能或薪資條件。")
    else:
        render_metrics(filtered_data)
        st.write("")
        overview_tab, skill_tab, salary_tab, report_tab, table_tab = st.tabs(
            ["市場總覽", "技能需求", "薪資與地區", "技能缺口報告", "職缺明細"]
        )
        with overview_tab:
            render_market_overview(filtered_data)
        with skill_tab:
            render_skills(filtered_data)
        with salary_tab:
            render_salary_location(filtered_data)
        with report_tab:
            render_skill_gap(filtered_data)
        with table_tab:
            render_table(filtered_data)
