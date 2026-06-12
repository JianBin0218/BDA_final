from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SkillPattern:
    canonical: str
    category: str
    aliases: tuple[str, ...]


SKILL_PATTERNS: tuple[SkillPattern, ...] = (
    SkillPattern("Python", "Programming Language", ("python", "py")),
    SkillPattern("JavaScript", "Programming Language", ("javascript", "js", "ecmascript")),
    SkillPattern("TypeScript", "Programming Language", ("typescript", "ts")),
    SkillPattern("Java", "Programming Language", ("java",)),
    SkillPattern("C#", "Programming Language", ("c#", "c sharp", "csharp")),
    SkillPattern("C/C++", "Programming Language", ("c++", "c/c++", "c language", "c語言")),
    SkillPattern("Golang", "Programming Language", ("golang", "go language", " go ", "go語言")),
    SkillPattern("PHP", "Programming Language", ("php",)),
    SkillPattern("Swift", "Programming Language", ("swift",)),
    SkillPattern("Kotlin", "Programming Language", ("kotlin",)),
    SkillPattern("React", "Frontend", ("react", "reactjs", "react.js")),
    SkillPattern("Vue", "Frontend", ("vue", "vuejs", "vue.js")),
    SkillPattern("Angular", "Frontend", ("angular", "angularjs")),
    SkillPattern("HTML/CSS", "Frontend", ("html", "css", "sass", "rwd")),
    SkillPattern("Node.js", "Backend", ("node.js", "nodejs", "node js")),
    SkillPattern("Spring Boot", "Backend", ("spring boot", "springboot")),
    SkillPattern("Django/FastAPI", "Backend", ("django", "fastapi", "flask")),
    SkillPattern("REST API", "Backend", ("restful", "rest api", "web api", "api串接", "api 開發")),
    SkillPattern("SQL", "Data", ("sql", "mysql", "postgresql", "postgres", "mssql", "ms sql")),
    SkillPattern("NoSQL", "Data", ("mongodb", "redis", "elasticsearch", "nosql")),
    SkillPattern("Data Engineering", "Data", ("data pipeline", "資料工程", "etl", "airflow", "spark", "kafka")),
    SkillPattern("Machine Learning", "AI/ML", ("machine learning", "機器學習", "ml", "深度學習", "deep learning")),
    SkillPattern("LLM/GenAI", "AI/ML", ("llm", "genai", "generative ai", "生成式 ai", "大型語言模型")),
    SkillPattern("PyTorch/TensorFlow", "AI/ML", ("pytorch", "tensorflow", "keras")),
    SkillPattern("Docker", "Cloud/DevOps", ("docker", "container", "容器化")),
    SkillPattern("Kubernetes", "Cloud/DevOps", ("kubernetes", "k8s")),
    SkillPattern("Cloud", "Cloud/DevOps", ("aws", "azure", "gcp", "雲端", "cloud")),
    SkillPattern("CI/CD", "Cloud/DevOps", ("ci/cd", "gitlab ci", "github actions", "jenkins")),
    SkillPattern("Linux", "Cloud/DevOps", ("linux", "ubuntu", "unix")),
    SkillPattern("Observability", "Cloud/DevOps", ("grafana", "prometheus", "elk", "monitoring")),
    SkillPattern("Cybersecurity", "Security", ("資安", "cybersecurity", "security", "滲透", "iso27001", "waf")),
    SkillPattern("Firmware/Embedded", "Embedded", ("韌體", "firmware", "embedded", "嵌入式", "rtos", "mcu")),
    SkillPattern("Mobile", "Mobile", ("ios", "android", "swiftui", "flutter", "react native")),
    SkillPattern("QA/Test", "QA", ("qa", "test", "測試", "selenium", "nunit", "vitest", "pytest")),
    SkillPattern("Git", "Tooling", ("git", "github", "gitlab")),
)


def extract_skills(*texts: object) -> list[str]:
    haystack = " ".join(str(text or "") for text in texts).lower()
    found: list[str] = []
    for pattern in SKILL_PATTERNS:
        if any(_contains_alias(haystack, alias.lower()) for alias in pattern.aliases):
            found.append(pattern.canonical)
    return found


def skill_categories(skills: list[str]) -> dict[str, str]:
    category_by_skill = {pattern.canonical: pattern.category for pattern in SKILL_PATTERNS}
    return {skill: category_by_skill.get(skill, "Other") for skill in skills}


def _contains_alias(text: str, alias: str) -> bool:
    if re.search(r"[\u4e00-\u9fff+#/.]", alias):
        return alias in text
    return re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", text) is not None
