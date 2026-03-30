"""ForgeDoc style system.

StyleConfig is the user-facing configuration. It produces ReportLab
ParagraphStyles and TableStyle commands via get_styles() and get_table_style().

Users override by passing a StyleConfig to render():
    style = StyleConfig(primary_color="#2d5f8a", body_size=10)
    render(doc, format="pdf", style=style)

All measurements in points (1 inch = 72 points).
"""

from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


@dataclass
class StyleConfig:
    """User-configurable style settings.

    Provides sensible defaults. Override any field to customize.
    """

    # Colors (hex strings)
    primary_color: str = "#1a1a2e"
    accent_color: str = "#16213e"
    header_bg: str = "#f0f0f5"
    row_alt: str = "#fafafa"
    border_color: str = "#cccccc"
    text_color: str = "#1a1a1a"
    muted_color: str = "#666666"

    # Typography
    font_family: str = "Helvetica"
    font_family_bold: str = "Helvetica-Bold"
    title_size: float = 18
    heading1_size: float = 14
    heading2_size: float = 12
    heading3_size: float = 10
    body_size: float = 9
    caption_size: float = 8
    cell_size: float = 8
    footer_size: float = 7

    # Spacing
    section_space_before: float = 18
    section_space_after: float = 8
    paragraph_space_after: float = 6
    table_cell_padding: float = 4
    table_cell_padding_h: float = 6

    def _c(self, hex_color: str):
        """Convert hex to ReportLab color."""
        return colors.HexColor(hex_color)

    @property
    def primary(self):
        return self._c(self.primary_color)

    @property
    def accent(self):
        return self._c(self.accent_color)

    @property
    def text(self):
        return self._c(self.text_color)

    @property
    def muted(self):
        return self._c(self.muted_color)

    @property
    def border(self):
        return self._c(self.border_color)


# Singleton default
DEFAULT_STYLE = StyleConfig()


def get_styles(config: StyleConfig | None = None) -> dict[str, ParagraphStyle]:
    """Build ReportLab ParagraphStyles from a StyleConfig."""
    c = config or DEFAULT_STYLE
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ForgeTitle",
            parent=base["Title"],
            fontName=c.font_family_bold,
            fontSize=c.title_size,
            leading=c.title_size + 4,
            textColor=c.primary,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "ForgeSubtitle",
            parent=base["Normal"],
            fontName=c.font_family,
            fontSize=c.body_size + 2,
            leading=c.body_size + 5,
            textColor=c.muted,
            spaceAfter=18,
        ),
        "heading1": ParagraphStyle(
            "ForgeH1",
            parent=base["Heading1"],
            fontName=c.font_family_bold,
            fontSize=c.heading1_size,
            leading=c.heading1_size + 4,
            textColor=c.primary,
            spaceBefore=c.section_space_before,
            spaceAfter=c.section_space_after,
        ),
        "heading2": ParagraphStyle(
            "ForgeH2",
            parent=base["Heading2"],
            fontName=c.font_family_bold,
            fontSize=c.heading2_size,
            leading=c.heading2_size + 3,
            textColor=c.accent,
            spaceBefore=c.section_space_before * 0.67,
            spaceAfter=c.section_space_after * 0.75,
        ),
        "heading3": ParagraphStyle(
            "ForgeH3",
            parent=base["Heading3"],
            fontName=c.font_family_bold,
            fontSize=c.heading3_size,
            leading=c.heading3_size + 3,
            textColor=c.accent,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "ForgeBody",
            parent=base["Normal"],
            fontName=c.font_family,
            fontSize=c.body_size,
            leading=c.body_size + 3,
            textColor=c.text,
            spaceAfter=c.paragraph_space_after,
        ),
        "body_bold": ParagraphStyle(
            "ForgeBodyBold",
            parent=base["Normal"],
            fontName=c.font_family_bold,
            fontSize=c.body_size,
            leading=c.body_size + 3,
            textColor=c.text,
            spaceAfter=c.paragraph_space_after,
        ),
        "caption": ParagraphStyle(
            "ForgeCaption",
            parent=base["Normal"],
            fontName=c.font_family,
            fontSize=c.caption_size,
            leading=c.caption_size + 2,
            textColor=c.muted,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "footer": ParagraphStyle(
            "ForgeFooter",
            parent=base["Normal"],
            fontName=c.font_family,
            fontSize=c.footer_size,
            leading=c.footer_size + 2,
            textColor=c.muted,
            alignment=TA_CENTER,
        ),
        "header_cell": ParagraphStyle(
            "ForgeHeaderCell",
            parent=base["Normal"],
            fontName=c.font_family_bold,
            fontSize=c.cell_size,
            leading=c.cell_size + 2,
            textColor=colors.white,
            alignment=TA_LEFT,
        ),
        "cell": ParagraphStyle(
            "ForgeCell",
            parent=base["Normal"],
            fontName=c.font_family,
            fontSize=c.cell_size,
            leading=c.cell_size + 2,
            textColor=c.text,
        ),
    }


def get_table_style(variant: str = "default", config: StyleConfig | None = None) -> list:
    """Build ReportLab TableStyle commands from a StyleConfig.

    Variants: "default" (full grid), "compact" (minimal lines), "striped" (no grid).
    """
    c = config or DEFAULT_STYLE
    pad = c.table_cell_padding
    pad_h = c.table_cell_padding_h

    if variant == "compact":
        return [
            ("BACKGROUND", (0, 0), (-1, 0), c._c(c.header_bg)),
            ("TEXTCOLOR", (0, 0), (-1, 0), c.primary),
            ("FONTNAME", (0, 0), (-1, 0), c.font_family_bold),
            ("FONTSIZE", (0, 0), (-1, -1), c.cell_size - 1),
            ("ALIGN", (0, 0), (-1, 0), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, 0), 1, c.primary),
            ("LINEBELOW", (0, -1), (-1, -1), 0.5, c.border),
            ("TOPPADDING", (0, 0), (-1, -1), pad * 0.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), pad * 0.5),
            ("LEFTPADDING", (0, 0), (-1, -1), pad_h * 0.67),
            ("RIGHTPADDING", (0, 0), (-1, -1), pad_h * 0.67),
        ]

    if variant == "striped":
        return [
            ("BACKGROUND", (0, 0), (-1, 0), c.primary),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), c.font_family_bold),
            ("FONTSIZE", (0, 0), (-1, 0), c.cell_size),
            ("FONTSIZE", (0, 1), (-1, -1), c.cell_size),
            ("ALIGN", (0, 0), (-1, 0), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c._c(c.row_alt)]),
            ("LINEBELOW", (0, 0), (-1, 0), 1, c.primary),
            ("TOPPADDING", (0, 0), (-1, -1), pad),
            ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
            ("LEFTPADDING", (0, 0), (-1, -1), pad_h),
            ("RIGHTPADDING", (0, 0), (-1, -1), pad_h),
        ]

    # default — full grid with alternating rows
    return [
        ("BACKGROUND", (0, 0), (-1, 0), c.primary),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), c.font_family_bold),
        ("FONTSIZE", (0, 0), (-1, 0), c.cell_size),
        ("FONTSIZE", (0, 1), (-1, -1), c.cell_size),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, c.border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c._c(c.row_alt)]),
        ("TOPPADDING", (0, 0), (-1, -1), pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
        ("LEFTPADDING", (0, 0), (-1, -1), pad_h),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad_h),
    ]
