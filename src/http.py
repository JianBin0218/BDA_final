from __future__ import annotations

import warnings
from typing import Any

import requests
import urllib3


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "SkillScope/1.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json,application/xhtml+xml,*/*",
}


def get_text(url: str, *, timeout: int = 30, **kwargs: Any) -> str:
    response = get(url, timeout=timeout, **kwargs)
    response.encoding = response.encoding or "utf-8"
    return response.text


def get_json(url: str, *, timeout: int = 30, **kwargs: Any) -> Any:
    return get(url, timeout=timeout, **kwargs).json()


def post_json(url: str, *, timeout: int = 30, **kwargs: Any) -> Any:
    headers = {**DEFAULT_HEADERS, "Accept": "application/json", **kwargs.pop("headers", {})}
    response = requests.post(url, headers=headers, timeout=timeout, **kwargs)
    response.raise_for_status()
    return response.json()


def get(url: str, *, timeout: int = 30, **kwargs: Any) -> requests.Response:
    headers = {**DEFAULT_HEADERS, **kwargs.pop("headers", {})}
    try:
        response = requests.get(url, headers=headers, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.SSLError:
        # Some Taiwan government endpoints have a certificate chain that fails
        # strict validation in the course conda image. Retry without verification
        # and make the fallback visible to callers through normal logs/warnings.
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        warnings.warn(f"SSL verification failed for {url}; retrying with verify=False")
        response = requests.get(url, headers=headers, timeout=timeout, verify=False, **kwargs)
        response.raise_for_status()
        return response
