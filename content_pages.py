"""content/*.md 프론트매터 파싱 + 마크다운 렌더링. plan/active/07-content-tooltips-monetization.md §4.1.

PyYAML 없이 동작하도록 'key: value' 줄 단위 프론트매터만 지원한다(콤마는 리스트 구분자).
콘텐츠가 전부 이 프로젝트 소유 파일이라 신뢰할 수 있는 입력이므로 간단한 파서로 충분하다.
"""

from __future__ import annotations

import os

import markdown as md

CONTENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta: dict[str, str] = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
        i += 1
    body = "\n".join(lines[i + 1:])
    return meta, body


def _split_list(value: str) -> list[str]:
    return [s.strip() for s in value.split(",") if s.strip()]


def load_content(slug: str) -> dict | None:
    """slug.md 하나를 읽어 렌더링된 dict를 반환. 파일이 없으면 None."""
    safe_slug = os.path.basename(slug)  # 경로 조작 방지
    path = os.path.join(CONTENT_DIR, f"{safe_slug}.md")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        text = f.read()
    meta, body = _parse_frontmatter(text)
    return {
        "slug": meta.get("slug", safe_slug),
        "title": meta.get("title", safe_slug),
        "description": meta.get("description", ""),
        "keywords": _split_list(meta.get("keywords", "")),
        "related": _split_list(meta.get("related", "")),
        "updated": meta.get("updated", ""),
        "html": md.markdown(body, extensions=["extra"]),
    }


def list_content() -> list[dict]:
    """content/ 디렉터리의 모든 글을 title 가나다순으로 정렬해 반환."""
    items = []
    for fname in os.listdir(CONTENT_DIR):
        if not fname.endswith(".md"):
            continue
        item = load_content(fname[:-3])
        if item:
            items.append(item)
    items.sort(key=lambda a: a["title"])
    return items
