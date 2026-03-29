"""Tests for ForgeDoc core functionality."""

import pytest
from forgedoc import Document, render
from forgedoc.core import Branding, PageConfig, Section, TableDef


class TestDocument:
    def test_create_empty_document(self):
        doc = Document(title="Test")
        assert doc.title == "Test"
        assert doc.sections == []

    def test_add_section(self):
        doc = Document(title="Test")
        sec = doc.add_section("Introduction", "Hello world")
        assert len(doc.sections) == 1
        assert sec.title == "Introduction"
        assert sec.content == "Hello world"

    def test_add_table(self):
        doc = Document(title="Test")
        doc.add_section("Data")
        table = doc.add_table(
            headers=["Name", "Value"],
            rows=[["Alpha", "1.0"], ["Beta", "2.0"]],
            caption="Test data",
        )
        assert len(doc.sections[0].tables) == 1
        assert table.caption == "Test data"
        assert len(table.rows) == 2

    def test_add_table_creates_section_if_empty(self):
        doc = Document(title="Test")
        doc.add_table(headers=["A"], rows=[["1"]])
        assert len(doc.sections) == 1

    def test_branding_defaults(self):
        branding = Branding()
        assert branding.company_name == ""
        assert branding.accent_color == "#1a1a2e"

    def test_page_config_defaults(self):
        config = PageConfig()
        assert config.size == "A4"


class TestRenderPDF:
    def test_render_simple_document(self):
        doc = Document(title="PDF Test", subtitle="Subtitle")
        doc.add_section("Section 1", "Some content here.")
        doc.add_table(headers=["Col A", "Col B"], rows=[["1", "2"], ["3", "4"]])

        result = render(doc, format="pdf")
        assert isinstance(result, bytes)
        assert result[:5] == b"%PDF-"
        assert len(result) > 100

    def test_render_with_branding(self):
        doc = Document(
            title="Branded Doc",
            branding=Branding(company_name="Acme Corp", footer_text="Confidential"),
        )
        doc.add_section("Content", "Branded content.")
        result = render(doc, format="pdf")
        assert result[:5] == b"%PDF-"

    def test_render_with_metadata(self):
        doc = Document(title="Meta Doc", metadata={"Author": "Jane", "Rev": "A"})
        doc.add_section("Body", "Content.")
        result = render(doc, format="pdf")
        assert result[:5] == b"%PDF-"

    def test_render_empty_document(self):
        doc = Document(title="Empty")
        result = render(doc, format="pdf")
        assert result[:5] == b"%PDF-"


class TestRenderHTML:
    def test_render_simple_html(self):
        doc = Document(title="HTML Test")
        doc.add_section("Intro", "Hello")
        result = render(doc, format="html")
        assert isinstance(result, str)
        assert "<h1>HTML Test</h1>" in result
        assert "Hello" in result

    def test_html_escapes_content(self):
        doc = Document(title="<script>alert('xss')</script>")
        result = render(doc, format="html")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_html_tables(self):
        doc = Document(title="Table Test")
        doc.add_section("Data")
        doc.add_table(headers=["X", "Y"], rows=[["1", "2"]])
        result = render(doc, format="html")
        assert "<table>" in result
        assert "<th>X</th>" in result


class TestRenderDOCX:
    def test_render_simple_docx(self):
        doc = Document(title="DOCX Test")
        doc.add_section("Section", "Content")
        result = render(doc, format="docx")
        assert isinstance(result, bytes)
        # DOCX files are ZIP archives
        assert result[:2] == b"PK"


class TestInvalidFormat:
    def test_unsupported_format_raises(self):
        doc = Document(title="Test")
        with pytest.raises(ValueError, match="Unsupported format"):
            render(doc, format="csv")
