import pytest

from ingestion.loaders import UnsupportedDocumentError, load_document


def test_load_markdown_preserves_title_and_source(tmp_path):
    path = tmp_path / "售后规则.md"
    path.write_text("# 售后规则\n七天内可申请退换。", encoding="utf-8")
    docs = load_document(path)
    assert docs[0].metadata["title"] == "售后规则"
    assert docs[0].metadata["source_file"] == "售后规则.md"
    assert "七天内" in docs[0].page_content


def test_load_text_uses_filename_as_title(tmp_path):
    path = tmp_path / "内容规范.txt"
    path.write_text("不得使用绝对化宣传用语。", encoding="utf-8")
    docs = load_document(path)
    assert docs[0].metadata["title"] == "内容规范"
    assert docs[0].metadata["content_type"] == "text"


def test_load_document_rejects_unknown_extension(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("a,b", encoding="utf-8")
    with pytest.raises(UnsupportedDocumentError):
        load_document(path)
