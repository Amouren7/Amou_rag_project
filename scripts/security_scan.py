from __future__ import annotations

import re
import subprocess
from pathlib import Path

PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{24,}"),
    re.compile(r"(?i)(app_secret|api_key|token|cookie)\s*[:=]\s*['\"]?[A-Za-z0-9_./+-]{20,}"),
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9_./+-]{20,}"),
)


def scan_paths(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            if (
                "sk-test" in line
                or "your_" in line.lower()
                or "settings." in line
                or "missing-api-key" in line
                or "os.getenv" in line
                or "security-test-fixture" in line
            ):
                continue
            if any(pattern.search(line) for pattern in PATTERNS):
                findings.append(f"{path}:{line_number}")
    return findings


def tracked_files() -> list[Path]:
    result = subprocess.run(["git", "ls-files"], check=True, capture_output=True, text=True)
    return [Path(line) for line in result.stdout.splitlines() if line]


if __name__ == "__main__":
    findings = scan_paths(tracked_files())
    if findings:
        print("Potential secrets found:")
        print("\n".join(findings))
        raise SystemExit(1)
    print("Security scan passed: no probable plaintext secrets found.")
