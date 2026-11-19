from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / "frontend" / "src" / "index.css").read_text()


def test_focus_visible_rule_is_present():
    assert ":focus-visible" in CSS
    assert "outline: 2px solid #018bff" in CSS
    assert "outline-offset: 2px" in CSS
