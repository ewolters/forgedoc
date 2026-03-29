"""PDF renderer using ReportLab platypus.

Converts a ForgeDoc Document into a paginated PDF with professional
styling, branding header/footer, and proper table handling.
"""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from reportlab.lib.pagesizes import A4, A3, letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)

from ..styles.default import get_styles, TABLE_STYLE_DEFAULT, TABLE_STYLE_COMPACT

if TYPE_CHECKING:
    from ..core import Document


_PAGE_SIZES = {
    "A4": A4,
    "a4": A4,
    "letter": letter,
    "A3": A3,
    "a3": A3,
    "A3-landscape": landscape(A3),
    "a3-landscape": landscape(A3),
}


def render_pdf(doc: Document, **kwargs) -> bytes:
    """Render a Document to PDF bytes."""
    buf = BytesIO()
    styles = get_styles()

    page_size = _PAGE_SIZES.get(doc.page_config.size, A4)
    pdf = SimpleDocTemplate(
        buf,
        pagesize=page_size,
        topMargin=doc.page_config.margin_top,
        bottomMargin=doc.page_config.margin_bottom,
        leftMargin=doc.page_config.margin_left,
        rightMargin=doc.page_config.margin_right,
        title=doc.title,
        author=doc.branding.company_name or "ForgeDoc",
    )

    flowables = []

    # Branding logo
    if doc.branding.logo_path:
        try:
            flowables.append(Image(doc.branding.logo_path, width=1.5 * inch, height=0.5 * inch))
            flowables.append(Spacer(1, 6))
        except Exception:
            pass  # Skip if logo can't be loaded
    elif doc.branding.logo_bytes:
        try:
            from io import BytesIO as _BIO

            flowables.append(Image(_BIO(doc.branding.logo_bytes), width=1.5 * inch, height=0.5 * inch))
            flowables.append(Spacer(1, 6))
        except Exception:
            pass

    # Title block
    flowables.append(Paragraph(doc.title, styles["title"]))
    if doc.subtitle:
        flowables.append(Paragraph(doc.subtitle, styles["subtitle"]))
    if doc.branding.company_name:
        flowables.append(Paragraph(doc.branding.company_name, styles["subtitle"]))
    flowables.append(Spacer(1, 12))

    # Metadata block (if present)
    if doc.metadata:
        meta_rows = [[str(k), str(v)] for k, v in doc.metadata.items() if v]
        if meta_rows:
            meta_table = Table(meta_rows, colWidths=[120, None])
            meta_table.setStyle(TableStyle(TABLE_STYLE_COMPACT))
            flowables.append(meta_table)
            flowables.append(Spacer(1, 12))

    # Sections
    for section in doc.sections:
        _render_section(section, flowables, styles)

    # Build with page number footer
    pdf.build(
        flowables,
        onFirstPage=_make_footer(doc),
        onLaterPages=_make_footer(doc),
    )

    return buf.getvalue()


def _render_section(section, flowables, styles):
    """Recursively render a section and its children."""
    if section.title:
        style_key = f"heading{min(section.level, 3)}"
        flowables.append(Paragraph(section.title, styles[style_key]))

    if section.content:
        for para in section.content.split("\n\n"):
            para = para.strip()
            if para:
                flowables.append(Paragraph(para, styles["body"]))

    for table_def in section.tables:
        _render_table(table_def, flowables, styles)

    for subsection in section.subsections:
        _render_section(subsection, flowables, styles)


def _render_table(table_def, flowables, styles):
    """Render a TableDef as a ReportLab Table."""
    # Build data rows with Paragraph wrapping for text flow
    data = [[Paragraph(str(h), styles["header_cell"]) for h in table_def.headers]]
    for row in table_def.rows:
        data.append([Paragraph(str(cell), styles["cell"]) for cell in row])

    col_widths = table_def.col_widths  # None = auto
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_cmds = TABLE_STYLE_COMPACT if table_def.style == "compact" else TABLE_STYLE_DEFAULT
    table.setStyle(TableStyle(style_cmds))

    flowables.append(table)

    if table_def.caption:
        flowables.append(Paragraph(table_def.caption, styles["caption"]))

    flowables.append(Spacer(1, 8))


def _make_footer(doc):
    """Create a page footer callback with page numbers and optional branding."""
    footer_text = doc.branding.footer_text or doc.title

    def _footer(canvas, pdf_doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColorRGB(0.4, 0.4, 0.4)

        page_width = pdf_doc.pagesize[0]
        # Left: document title / branding
        canvas.drawString(
            pdf_doc.leftMargin,
            20,
            footer_text[:80],
        )
        # Right: page number
        canvas.drawRightString(
            page_width - pdf_doc.rightMargin,
            20,
            f"Page {canvas.getPageNumber()}",
        )
        canvas.restoreState()

    return _footer
