"""Tests for style configuration and multi-page rendering."""

from forgedoc import Document, render
from forgedoc.core import TableDef
from forgedoc.styles.default import StyleConfig, get_styles, get_table_style


class TestStyleConfig:
    def test_default_style(self):
        config = StyleConfig()
        assert config.primary_color == "#1a1a2e"
        assert config.body_size == 9

    def test_custom_colors(self):
        config = StyleConfig(primary_color="#ff0000", accent_color="#00ff00")
        styles = get_styles(config)
        assert styles["title"].textColor is not None

    def test_custom_font_sizes(self):
        config = StyleConfig(title_size=24, body_size=12, cell_size=10)
        styles = get_styles(config)
        assert styles["title"].fontSize == 24
        assert styles["body"].fontSize == 12
        assert styles["cell"].fontSize == 10

    def test_table_style_variants(self):
        config = StyleConfig()
        default = get_table_style("default", config)
        compact = get_table_style("compact", config)
        striped = get_table_style("striped", config)
        assert len(default) > 0
        assert len(compact) > 0
        assert len(striped) > 0
        # Default has GRID command, compact doesn't
        default_cmds = [c[0] for c in default]
        compact_cmds = [c[0] for c in compact]
        assert "GRID" in default_cmds
        assert "GRID" not in compact_cmds

    def test_custom_style_renders_pdf(self):
        """Custom style produces valid PDF."""
        config = StyleConfig(
            primary_color="#2d5f8a",
            accent_color="#1a4a6e",
            body_size=10,
            cell_size=9,
        )
        doc = Document(title="Custom Styled")
        doc.add_section("Section", "Body text with custom style.")
        doc.add_table(headers=["A", "B"], rows=[["1", "2"]])

        result = render(doc, format="pdf", style=config)
        assert result[:5] == b"%PDF-"


class TestMultiPageTable:
    def test_large_table_renders(self):
        """100-row table should produce a multi-page PDF without crashing."""
        doc = Document(title="Large Table Test")
        sec = doc.add_section("Data")
        sec.tables.append(TableDef(
            headers=["Row", "Value A", "Value B", "Description"],
            rows=[
                [str(i), f"{i * 1.1:.2f}", f"{i * 2.3:.2f}", f"Row {i} description text"]
                for i in range(100)
            ],
        ))

        result = render(doc, format="pdf")
        assert result[:5] == b"%PDF-"
        # Multi-page PDF should be larger than a single-page one
        assert len(result) > 5000

    def test_very_large_table_renders(self):
        """500-row table stress test."""
        doc = Document(title="Stress Test")
        sec = doc.add_section("Big Data")
        sec.tables.append(TableDef(
            headers=["ID", "Measurement", "Tolerance", "Result", "Notes"],
            rows=[
                [str(i), f"{50 + i * 0.01:.3f}", "50.0 ± 0.5", "PASS" if i % 7 != 0 else "FAIL",
                 f"Sample from batch {i // 50}"]
                for i in range(500)
            ],
        ))

        result = render(doc, format="pdf")
        assert result[:5] == b"%PDF-"

    def test_large_table_docx(self):
        """Large table in DOCX format."""
        doc = Document(title="DOCX Table Test")
        sec = doc.add_section("Data")
        sec.tables.append(TableDef(
            headers=["A", "B", "C"],
            rows=[[str(i), str(i * 2), str(i * 3)] for i in range(100)],
        ))

        result = render(doc, format="docx")
        assert result[:2] == b"PK"  # DOCX is a ZIP

    def test_multiple_tables_and_sections(self):
        """Document with multiple sections and tables."""
        doc = Document(title="Complex Document")
        for s in range(5):
            sec = doc.add_section(f"Section {s + 1}", f"Introduction to section {s + 1}.")
            sec.tables.append(TableDef(
                headers=["Metric", "Target", "Actual"],
                rows=[[f"M{s}{i}", f"{80 + i}", f"{78 + i + s}"] for i in range(10)],
            ))

        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"

        html = render(doc, format="html")
        assert html.count("<table>") == 5

        docx = render(doc, format="docx")
        assert docx[:2] == b"PK"
