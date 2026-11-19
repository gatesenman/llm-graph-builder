from pathlib import Path

from src.offline_preview import preview_file, preview_text

FIXTURE = Path(__file__).parent / "fixtures" / "sample_graph.txt"


def test_preview_file_builds_nodes_and_edges_without_neo4j():
    graph = preview_file(FIXTURE)
    assert graph["kind"] == "offline-graph-preview"
    names = {n["name"] for n in graph["nodes"]}
    assert "Alice Chen" in names
    assert "Northwind Labs" in names
    types = {e["type"] for e in graph["edges"]}
    assert "IS_A" in types
    assert "WORKS_AT" in types
    # fixture text only, no connection strings or passwords
    dumped = str(graph)
    assert "password" not in dumped.lower()
    assert "neo4j" not in dumped.lower()


def test_preview_text_handles_empty_input():
    graph = preview_text("   ")
    assert graph["nodes"] == []
    assert graph["edges"] == []
