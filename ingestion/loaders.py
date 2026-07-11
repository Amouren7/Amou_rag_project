from __future__ import annotations

from pathlib import Path
import re

from langchain_core.documents import Document


class UnsupportedDocumentError(ValueError):
    pass


def load_document(path: str | Path) -> list[Document]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    suffix = file_path.suffix.lower()
    if suffix in {".md", ".txt"}:
        content = file_path.read_text(encoding="utf-8-sig").strip()
        title = file_path.stem
        if suffix == ".md":
            match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if match:
                title = match.group(1).strip()
        return [Document(page_content=content, metadata={
            "title": title,
            "source": str(file_path),
            "source_file": file_path.name,
            "content_type": "markdown" if suffix == ".md" else "text",
            "page_number": 1,
        })]
    if suffix == ".pdf":
        from .extract_files import create_pdf_extractor
        content, metadata = create_pdf_extractor().extract_pdf_content(str(file_path))
        metadata.update({"source_file": file_path.name, "page_number": 1})
        return [Document(page_content=content, metadata=metadata)]
    raise UnsupportedDocumentError(f"Unsupported document type: {suffix or '<none>'}")
