from pathlib import Path

from scripts.security_scan import scan_paths


def test_security_scan_flags_probable_secret(tmp_path):
    path = tmp_path / "bad.env"
    path.write_text("API_KEY=sk-abcdefghijklmnopqrstuvwxyz123456", encoding="utf-8")  # security-test-fixture
    findings = scan_paths([path])
    assert findings


def test_security_scan_allows_empty_example_values(tmp_path):
    path = tmp_path / ".env.example"
    path.write_text("LLM_API_KEY=\nEMBEDDING_API_KEY=\n", encoding="utf-8")
    assert scan_paths([path]) == []
