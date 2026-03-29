"""DOCX renderer using python-docx.

Requires the optional 'docx' dependency: pip install forgedoc[docx]
"""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Document


def render_docx(doc: Document, **kwargs) -> bytes:
    """Render a Document to DOCX bytes."""
    try:
        from docx import Document as DocxDocument
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        raise ImportError(
            "python-docx is required for DOCX output. "
            "Install it with: pip install forgedoc[docx]"
        )

    docx = DocxDocument()

    # Title
    title_para = docx.add_heading(doc.title, level=0)
    if doc.subtitle:
        sub = docx.add_paragraph(doc.subtitle)
        sub.style = docx.styles["Subtitle"]

    # Branding
    if doc.branding.company_name:
        p = docx.add_paragraph(doc.branding.company_name)
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.color.rgb = None  # Use theme color

    # Metadata
    if doc.metadata:
        table = docx.add_table(rows=0, cols=2)
        table.style = "Light List"
        for k, v in doc.metadata.items():
            if v:
                row = table.add_row()
                row.cells[0].text = str(k)
                row.cells[1].text = str(v)
        docx.add_paragraph()  # Spacer

    # Sections
    for section in doc.sections:
        _render_section_docx(docx, section)

    buf = BytesIO()
    docx.save(buf)
    return buf.getvalue()


def _render_section_docx(docx, section):
    """Render a section into the DOCX document."""
    if section.title:
        docx.add_heading(section.title, level=min(section.level, 4))

    if section.content:
        for para in section.content.split("\n\n"):
            para = para.strip()
            if para:
                docx.add_paragraph(para)

    for table_def in section.tables:
        table = docx.add_table(rows=1, cols=len(table_def.headers))
        table.style = "Light Grid Accent 1"

        # Header row
        for i, h in enumerate(table_def.headers):
            table.rows[0].cells[i].text = str(h)

        # Data rows
        for row_data in table_def.rows:
            row = table.add_row()
            for i, cell in enumerate(row_data):
                if i < len(row.cells):
                    row.cells[i].text = str(cell)

        if table_def.caption:
            p = docx.add_paragraph(table_def.caption)
            from docx.shared import Pt

            p.runs[0].font.size = Pt(8) if p.runs else None

    for sub in section.subsections:
        _render_section_docx(docx, sub)
