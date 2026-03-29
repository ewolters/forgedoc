"""Core document model and render entry point.

ForgeDoc documents are built programmatically from sections, tables,
images, and metadata. Rendering is deferred — the document is a data
structure until render() is called with a target format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Branding:
    """Tenant/organization branding for document headers and footers."""

    company_name: str = ""
    logo_bytes: bytes | None = None
    logo_path: str | None = None
    accent_color: str = "#1a1a2e"
    footer_text: str = ""


@dataclass
class TableDef:
    """A table to be rendered in a document."""

    headers: list[str]
    rows: list[list[Any]]
    col_widths: list[float] | None = None
    caption: str = ""
    style: str = "default"  # "default", "compact", "striped"


@dataclass
class Section:
    """A document section with optional content types."""

    title: str
    content: str = ""
    level: int = 1  # Heading level (1-4)
    tables: list[TableDef] = field(default_factory=list)
    subsections: list[Section] = field(default_factory=list)


@dataclass
class PageConfig:
    """Page layout configuration."""

    size: str = "A4"  # "A4", "letter", "A3", "A3-landscape"
    margin_top: float = 72  # points (1 inch)
    margin_bottom: float = 72
    margin_left: float = 54
    margin_right: float = 54


@dataclass
class Document:
    """A ForgeDoc document — the universal data structure for all output formats.

    Build a document by adding sections, tables, and metadata.
    Render to PDF, DOCX, or HTML by calling render().
    """

    title: str
    subtitle: str = ""
    doc_type: str = ""  # For registry/template identification
    sections: list[Section] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    branding: Branding = field(default_factory=Branding)
    page_config: PageConfig = field(default_factory=PageConfig)

    def add_section(self, title: str, content: str = "", level: int = 1) -> Section:
        """Add a section to the document."""
        section = Section(title=title, content=content, level=level)
        self.sections.append(section)
        return section

    def add_table(
        self,
        headers: list[str],
        rows: list[list[Any]],
        caption: str = "",
        col_widths: list[float] | None = None,
    ) -> TableDef:
        """Add a standalone table (appended to last section, or creates one)."""
        table = TableDef(headers=headers, rows=rows, caption=caption, col_widths=col_widths)
        if not self.sections:
            self.add_section("")
        self.sections[-1].tables.append(table)
        return table


def render(doc: Document, format: str = "pdf", **kwargs) -> bytes | str:
    """Render a Document to the specified format.

    Args:
        doc: The Document to render.
        format: Output format — "pdf", "docx", or "html".

    Returns:
        bytes for pdf/docx, str for html.
    """
    if format == "pdf":
        from .renderers.pdf import render_pdf

        return render_pdf(doc, **kwargs)
    elif format == "docx":
        from .renderers.docx import render_docx

        return render_docx(doc, **kwargs)
    elif format == "html":
        from .renderers.html import render_html

        return render_html(doc, **kwargs)
    else:
        raise ValueError(f"Unsupported format: {format!r}. Use 'pdf', 'docx', or 'html'.")
