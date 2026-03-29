"""PDF renderer using ReportLab platypus.

Converts a ForgeDoc Document into a paginated PDF with professional
styling, branding header/footer, and proper table handling.
"""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from reportlab.lib.pagesizes import A3, A4, letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ..styles.default import StyleConfig, get_styles, get_table_style

if TYPE_CHECKING:
    from ..core import Document, Section, TableDef


_PAGE_SIZES = {
    "A4": A4,
    "a4": A4,
    "letter": letter,
    "A3": A3,
    "a3": A3,
    "A3-landscape": landscape(A3),
    "a3-landscape": landscape(A3),
    "A4-landscape": landscape(A4),
    "a4-landscape": landscape(A4),
}


def render_pdf(doc: Document, style: StyleConfig | None = None, **kwargs) -> bytes:
    """Render a Document to PDF bytes.

    Args:
        doc: The Document to render.
        style: Optional StyleConfig override. Uses defaults if not provided.
    """
    buf = BytesIO()
    config = style or StyleConfig()
    styles = get_styles(config)

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

    flowables: list = []

    # Branding logo
    _add_logo(flowables, doc)

    # Title block
    flowables.append(Paragraph(doc.title, styles["title"]))
    if doc.subtitle:
        flowables.append(Paragraph(doc.subtitle, styles["subtitle"]))
    if doc.branding.company_name:
        flowables.append(Paragraph(doc.branding.company_name, styles["subtitle"]))
    flowables.append(Spacer(1, 12))

    # Metadata block
    if doc.metadata:
        meta_rows = []
        for k, v in doc.metadata.items():
            if v:
                meta_rows.append([
                    Paragraph(f"<b>{k}</b>", styles["cell"]),
                    Paragraph(str(v), styles["cell"]),
                ])
        if meta_rows:
            meta_table = Table(meta_rows, colWidths=[120, None])
            meta_table.setStyle(TableStyle(get_table_style("compact", config)))
            flowables.append(meta_table)
            flowables.append(Spacer(1, 12))

    # Sections
    for section in doc.sections:
        _render_section(section, flowables, styles, config)

    # Build PDF with page number footer
    pdf.build(
        flowables,
        onFirstPage=_make_footer(doc, config),
        onLaterPages=_make_footer(doc, config),
    )

    return buf.getvalue()


def _add_logo(flowables: list, doc: Document):
    """Add branding logo if available."""
    if doc.branding.logo_path:
        try:
            flowables.append(Image(doc.branding.logo_path, width=1.5 * inch, height=0.5 * inch))
            flowables.append(Spacer(1, 6))
        except Exception:
            pass
    elif doc.branding.logo_bytes:
        try:
            flowables.append(
                Image(BytesIO(doc.branding.logo_bytes), width=1.5 * inch, height=0.5 * inch)
            )
            flowables.append(Spacer(1, 6))
        except Exception:
            pass


def _render_section(
    section: Section, flowables: list, styles: dict, config: StyleConfig
):
    """Recursively render a section and its children."""
    if section.title:
        style_key = f"heading{min(section.level, 3)}"
        flowables.append(Paragraph(section.title, styles[style_key]))

    if section.content:
        from ..markdown import md_to_reportlab

        for para_xml in md_to_reportlab(section.content):
            flowables.append(Paragraph(para_xml, styles["body"]))

    for table_def in section.tables:
        _render_table(table_def, flowables, styles, config)

    for subsection in section.subsections:
        _render_section(subsection, flowables, styles, config)


def _render_table(
    table_def: TableDef, flowables: list, styles: dict, config: StyleConfig
):
    """Render a TableDef as a ReportLab Table with proper pagination."""
    # Build data rows with Paragraph wrapping for text flow
    data = [[Paragraph(str(h), styles["header_cell"]) for h in table_def.headers]]
    for row in table_def.rows:
        data.append([Paragraph(str(cell), styles["cell"]) for cell in row])

    table = Table(data, colWidths=table_def.col_widths, repeatRows=1)
    style_cmds = get_table_style(table_def.style, config)
    table.setStyle(TableStyle(style_cmds))

    # For small tables (< 10 rows), try to keep together on one page
    if len(table_def.rows) < 10:
        flowables.append(KeepTogether([table]))
    else:
        flowables.append(table)

    if table_def.caption:
        flowables.append(Paragraph(table_def.caption, styles["caption"]))

    flowables.append(Spacer(1, 8))


def _make_footer(doc: Document, config: StyleConfig):
    """Create a page footer callback with page numbers and optional branding."""
    footer_text = doc.branding.footer_text or doc.title

    def _footer(canvas, pdf_doc):
        canvas.saveState()
        canvas.setFont(config.font_family, config.footer_size)
        canvas.setFillColorRGB(0.4, 0.4, 0.4)

        page_width = pdf_doc.pagesize[0]
        y = 20

        # Left: document title / branding
        canvas.drawString(pdf_doc.leftMargin, y, footer_text[:80])

        # Right: page number
        canvas.drawRightString(
            page_width - pdf_doc.rightMargin,
            y,
            f"Page {canvas.getPageNumber()}",
        )
        canvas.restoreState()

    return _footer
