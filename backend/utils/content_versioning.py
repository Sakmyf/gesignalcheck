# backend/utils/content_versioning.py

import hashlib
from difflib import SequenceMatcher


def generate_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_analysis_key(url: str, content_hash: str, engine_version: str, prompt_version: str) -> str:
    base = f"{url}-{content_hash}-{engine_version}-{prompt_version}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def similarity_ratio(old_text: str, new_text: str) -> float:
    return SequenceMatcher(None, old_text, new_text).ratio()


def detect_change_level(old_text: str, new_text: str) -> str:
    ratio = similarity_ratio(old_text, new_text)

    if ratio > 0.95:
        return "minimal"
    elif ratio > 0.80:
        return "moderate"
    else:
        return "significant"