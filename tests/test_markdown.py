"""Tests for markdown parsing and rendering across all formats."""

from forgedoc import Document, render
from forgedoc.markdown import md_to_reportlab, md_to_html, md_to_plain


class TestMarkdownToReportlab:
    def test_bold(self):
        result = md_to_reportlab("This is **bold** text.")
        assert len(result) == 1
        assert "<b>bold</b>" in result[0]

    def test_italic(self):
        result = md_to_reportlab("This is *italic* text.")
        assert "<i>italic</i>" in result[0]

    def test_inline_code(self):
        result = md_to_reportlab("Use `F()` expressions.")
        assert "Courier" in result[0]
        assert "F()" in result[0]

    def test_link(self):
        result = md_to_reportlab("See [docs](https://example.com).")
        assert "href" in result[0]
        assert "docs" in result[0]

    def test_bullet_list(self):
        text = "- Item one\n- Item two\n- Item three"
        result = md_to_reportlab(text)
        assert len(result) == 3
        assert "\u2022" in result[0]

    def test_numbered_list(self):
        text = "1. First\n2. Second\n3. Third"
        result = md_to_reportlab(text)
        assert len(result) == 3

    def test_multiple_paragraphs(self):
        text = "First paragraph.\n\nSecond paragraph."
        result = md_to_reportlab(text)
        assert len(result) == 2

    def test_empty_input(self):
        assert md_to_reportlab("") == []
        assert md_to_reportlab(None) == []

    def test_mixed_formatting(self):
        text = "This has **bold** and *italic* and `code` in one line."
        result = md_to_reportlab(text)
        assert "<b>bold</b>" in result[0]
        assert "<i>italic</i>" in result[0]


class TestMarkdownToHtml:
    def test_paragraph(self):
        result = md_to_html("Hello world.")
        assert "<p>" in result
        assert "Hello world." in result

    def test_bold(self):
        result = md_to_html("This is **bold**.")
        assert "<strong>bold</strong>" in result

    def test_italic(self):
        result = md_to_html("This is *italic*.")
        assert "<em>italic</em>" in result

    def test_bullet_list(self):
        result = md_to_html("- One\n- Two")
        assert "<ul>" in result
        assert "<li>" in result

    def test_numbered_list(self):
        result = md_to_html("1. One\n2. Two")
        assert "<ol>" in result

    def test_link(self):
        result = md_to_html("Click [here](https://example.com).")
        assert '<a href="https://example.com">here</a>' in result

    def test_code(self):
        result = md_to_html("Use `render()` function.")
        assert "<code>render()</code>" in result

    def test_escapes_html(self):
        result = md_to_html("Use <script>alert('xss')</script>.")
        assert "<script>" not in result


class TestMarkdownToPlain:
    def test_strips_bold(self):
        assert md_to_plain("This is **bold** text.") == "This is bold text."

    def test_strips_italic(self):
        assert md_to_plain("This is *italic*.") == "This is italic."

    def test_strips_code(self):
        assert md_to_plain("Use `F()`.") == "Use F()."

    def test_strips_links(self):
        assert md_to_plain("See [docs](https://x.com).") == "See docs."

    def test_empty(self):
        assert md_to_plain("") == ""


class TestMarkdownInRenderers:
    def test_pdf_renders_markdown(self):
        doc = Document(title="MD Test")
        doc.add_section("Section", "This has **bold** and *italic* and `code`.\n\n- Bullet one\n- Bullet two")
        result = render(doc, format="pdf")
        assert result[:5] == b"%PDF-"

    def test_html_renders_markdown(self):
        doc = Document(title="MD Test")
        doc.add_section("Section", "This has **bold** text.\n\n1. First\n2. Second")
        result = render(doc, format="html")
        assert "<strong>bold</strong>" in result
        assert "<ol>" in result

    def test_docx_renders_markdown(self):
        doc = Document(title="MD Test")
        doc.add_section("Section", "This has **bold** and *italic*.\n\n- Bullet A\n- Bullet B")
        result = render(doc, format="docx")
        assert result[:2] == b"PK"

    def test_investigation_with_markdown(self):
        """Real-world: investigation report with markdown content."""
        from forgedoc.builders.investigation import InvestigationReport

        report = InvestigationReport(title="Test")
        report.add_scope(
            "**CNC machining center** → surface finish → dimensional tolerance\n\n"
            "Key parameters:\n"
            "- Coolant viscosity (`cSt`)\n"
            "- Spindle speed (*RPM*)\n"
            "- Feed rate"
        )
        report.add_root_cause("Coolant viscosity **degrades** after 4hr continuous run")
        doc = report.to_document()

        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"

        html = render(doc, format="html")
        assert "<strong>CNC machining center</strong>" in html
