"""Default style definitions for ForgeDoc documents.

All measurements in points (1 inch = 72 points).
Colors as hex strings.
"""

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Color palette — professional, readable, printer-friendly
PRIMARY = colors.HexColor("#1a1a2e")
ACCENT = colors.HexColor("#16213e")
HEADER_BG = colors.HexColor("#f0f0f5")
ROW_ALT = colors.HexColor("#fafafa")
BORDER = colors.HexColor("#cccccc")
TEXT = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#666666")


def get_styles() -> dict:
    """Return the full style dictionary for document rendering."""
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ForgeTitle",
            parent=base["Title"],
            fontSize=18,
            leading=22,
            textColor=PRIMARY,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "ForgeSubtitle",
            parent=base["Normal"],
            fontSize=11,
            leading=14,
            textColor=MUTED,
            spaceAfter=18,
        ),
        "heading1": ParagraphStyle(
            "ForgeH1",
            parent=base["Heading1"],
            fontSize=14,
            leading=18,
            textColor=PRIMARY,
            spaceBefore=18,
            spaceAfter=8,
        ),
        "heading2": ParagraphStyle(
            "ForgeH2",
            parent=base["Heading2"],
            fontSize=12,
            leading=15,
            textColor=ACCENT,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "heading3": ParagraphStyle(
            "ForgeH3",
            parent=base["Heading3"],
            fontSize=10,
            leading=13,
            textColor=ACCENT,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "ForgeBody",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            textColor=TEXT,
            spaceAfter=6,
        ),
        "caption": ParagraphStyle(
            "ForgeCaption",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "footer": ParagraphStyle(
            "ForgeFooter",
            parent=base["Normal"],
            fontSize=7,
            leading=9,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "header_cell": ParagraphStyle(
            "ForgeHeaderCell",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.white,
            alignment=TA_LEFT,
        ),
        "cell": ParagraphStyle(
            "ForgeCell",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
            textColor=TEXT,
        ),
    }


# Table style commands for ReportLab Table objects
TABLE_STYLE_DEFAULT = [
    ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, 0), 8),
    ("FONTSIZE", (0, 1), (-1, -1), 8),
    ("ALIGN", (0, 0), (-1, 0), "LEFT"),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
]

TABLE_STYLE_COMPACT = [
    ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
    ("TEXTCOLOR", (0, 0), (-1, 0), PRIMARY),
    ("FONTSIZE", (0, 0), (-1, -1), 7),
    ("ALIGN", (0, 0), (-1, 0), "LEFT"),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LINEBELOW", (0, 0), (-1, 0), 1, PRIMARY),
    ("LINEBELOW", (0, -1), (-1, -1), 0.5, BORDER),
    ("TOPPADDING", (0, 0), (-1, -1), 2),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
]
