from __future__ import annotations

import re


CLUSTERS = (
    "Backend / Full-stack",
    "Frontend",
    "Data / AI",
    "Cloud / DevOps / SRE",
    "Cybersecurity",
    "Firmware / Embedded",
    "QA / Test",
    "MIS / IT Support",
    "Mobile",
    "Other CS",
)


def classify_cluster(title: object, description: object, skills: list[str]) -> str:
    text = f"{title or ''} {description or ''}".lower()
    skill_set = set(skills)

    if _has(text, ("資安", "security", "cyber", "滲透")) or "Cybersecurity" in skill_set:
        return "Cybersecurity"
    if _has(text, ("韌體", "firmware", "embedded", "嵌入式")) or "Firmware/Embedded" in skill_set:
        return "Firmware / Embedded"
    if _has(text, ("devops", "sre", "cloud", "雲端", "kubernetes", "k8s")) or skill_set & {
        "Cloud",
        "Kubernetes",
        "Docker",
        "CI/CD",
    }:
        return "Cloud / DevOps / SRE"
    if _has(text, ("data", "資料", "machine learning", "機器學習")) or re.search(r"(?<![a-z0-9])ai(?![a-z0-9])", text) or skill_set & {
        "Data Engineering",
        "Machine Learning",
        "LLM/GenAI",
        "PyTorch/TensorFlow",
    }:
        return "Data / AI"
    if _has(text, ("frontend", "front-end", "前端", "ui", "web designer")) or skill_set & {
        "React",
        "Vue",
        "Angular",
        "HTML/CSS",
    }:
        return "Frontend"
    if _has(text, ("ios", "android", "mobile", "app工程師")) or "Mobile" in skill_set:
        return "Mobile"
    if _has(text, ("qa", "test", "測試", "品保")) or "QA/Test" in skill_set:
        return "QA / Test"
    if _has(text, ("mis", "it support", "系統管理", "網管", "資訊人員")):
        return "MIS / IT Support"
    if _has(text, ("backend", "back-end", "後端", "full stack", "full-stack", "全端", "software engineer", "程式設計")):
        return "Backend / Full-stack"
    return "Other CS"


def _has(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
