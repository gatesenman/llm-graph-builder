"""Deterministic offline graph preview. No Neo4j, no LLM, no secrets."""

from __future__ import annotations

import re
from pathlib import Path

_SENTENCE = re.compile(r"(?<=[.!?。！？])\s+")
_IS_A = re.compile(
    r"^\s*(?P<source>[A-Z][\w .'-]{1,80}?)\s+(?:is|are|was|were)\s+(?:an?\s+)?(?P<label>[A-Za-z][\w '-]{1,80})\s*$",
    re.IGNORECASE,
)
_WORKS = re.compile(
    r"^\s*(?P<source>[A-Z][\w .'-]{1,80}?)\s+works\s+(?:at|for)\s+(?P<target>[A-Z][\w .'-]{1,80}?)\s*$",
    re.IGNORECASE,
)
_PROPER = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b")


def _norm(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip()


def preview_text(text: str, source: str = "fixture") -> dict:
    """Turn local text into a graph JSON document (nodes/edges)."""
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def add_node(name: str, label: str = "Entity") -> str:
        name = _norm(name)
        key = name.lower()
        if key not in nodes:
            nodes[key] = {"id": f"n{len(nodes) + 1}", "name": name, "label": label}
        elif label not in {"Entity"} and nodes[key]["label"] == "Entity":
            nodes[key]["label"] = label
        return nodes[key]["id"]

    parts = _SENTENCE.split(text.strip()) if text.strip() else []
    for raw in parts:
        sentence = raw.strip().strip(".")
        if not sentence:
            continue
        is_a = _IS_A.match(sentence)
        if is_a:
            sid = add_node(is_a.group("source"))
            tid = add_node(_norm(is_a.group("label")).title(), "Type")
            edges.append({"source": sid, "target": tid, "type": "IS_A", "label": "is_a"})
            continue
        works = _WORKS.match(sentence)
        if works:
            sid = add_node(works.group("source"))
            tid = add_node(works.group("target"), "Organization")
            edges.append({"source": sid, "target": tid, "type": "WORKS_AT", "label": "works_at"})
            continue
        for name in _PROPER.findall(sentence):
            add_node(name)

    return {
        "kind": "offline-graph-preview",
        "source": source,
        "nodes": list(nodes.values()),
        "edges": edges,
    }


def preview_file(path: Path) -> dict:
    return preview_text(path.read_text(encoding="utf-8"), source=path.name)
