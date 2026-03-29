"""Lightweight markdown parser for ForgeDoc.

Converts a subset of markdown to ReportLab-compatible XML markup
and plain text for DOCX. No external dependencies.

Supported:
- **bold** and *italic*
- Bullet lists (- item or * item)
- Numbered lists (1. item)
- `inline code`
- [links](url) — rendered as underlined text in PDF, hyperlink in HTML
- Line breaks (double newline = new paragraph)

Not supported (intentionally):
- Headers (use Document sections instead)
- Images (use Document.add_image() instead)
- Tables (use Document.add_table() instead)
- HTML passthrough
"""

from __future__ import annotations

import re


def md_to_reportlab(text: str) -> list[str]:
    """Convert markdown text to a list of ReportLab XML paragraphs.

    Each paragraph is a string suitable for Paragraph(text, style).
    ReportLab uses a subset of HTML-like tags: <b>, <i>, <font>, <a>, <br/>.
    """
    if not text:
        return []

    paragraphs = []
    current_list = []
    list_type = None  # "bullet" or "numbered"

    for block in re.split(r"\n{2,}", text.strip()):
        lines = block.strip().split("\n")

        # Check if this block is a list
        is_list_block = all(
            re.match(r"^[\-\*]\s+", line.strip()) or re.match(r"^\d+\.\s+", line.strip())
            for line in lines
            if line.strip()
        )

        if is_list_block:
            list_items = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Strip bullet/number prefix
                item_text = re.sub(r"^[\-\*]\s+", "", line)
                item_text = re.sub(r"^\d+\.\s+", "", item_text)
                item_text = _inline_markup(item_text)

                if re.match(r"^\d+\.\s+", line):
                    list_items.append(f"<seq/>. {item_text}")
                else:
                    list_items.append(f"\u2022 {item_text}")

            paragraphs.extend(list_items)
        else:
            # Regular paragraph — join lines, apply inline markup
            joined = " ".join(line.strip() for line in lines if line.strip())
            if joined:
                paragraphs.append(_inline_markup(joined))

    return paragraphs


def md_to_plain(text: str) -> str:
    """Convert markdown to plain text (for DOCX runs).

    Strips markdown syntax, preserves structure.
    """
    if not text:
        return ""

    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)  # italic
    text = re.sub(r"`(.+?)`", r"\1", text)  # code
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)  # links
    return text


def md_to_html(text: str) -> str:
    """Convert markdown to HTML (for HTML renderer).

    Produces semantic HTML — <strong>, <em>, <code>, <a>, <ul>/<ol>.
    """
    if not text:
        return ""

    blocks = re.split(r"\n{2,}", text.strip())
    html_parts = []

    for block in blocks:
        lines = block.strip().split("\n")

        # Check if list
        is_bullet = all(re.match(r"^[\-\*]\s+", l.strip()) for l in lines if l.strip())
        is_numbered = all(re.match(r"^\d+\.\s+", l.strip()) for l in lines if l.strip())

        if is_bullet:
            items = []
            for line in lines:
                item = re.sub(r"^[\-\*]\s+", "", line.strip())
                items.append(f"<li>{_inline_html(item)}</li>")
            html_parts.append("<ul>" + "".join(items) + "</ul>")
        elif is_numbered:
            items = []
            for line in lines:
                item = re.sub(r"^\d+\.\s+", "", line.strip())
                items.append(f"<li>{_inline_html(item)}</li>")
            html_parts.append("<ol>" + "".join(items) + "</ol>")
        else:
            joined = " ".join(l.strip() for l in lines if l.strip())
            if joined:
                html_parts.append(f"<p>{_inline_html(joined)}</p>")

    return "\n".join(html_parts)


def _inline_markup(text: str) -> str:
    """Apply inline markdown → ReportLab XML."""
    # Bold: **text** → <b>text</b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic: *text* → <i>text</i>
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Code: `text` → <font face="Courier" size="8">text</font>
    text = re.sub(r"`(.+?)`", r'<font face="Courier" size="8">\1</font>', text)
    # Links: [text](url) → <a href="url" color="blue"><u>text</u></a>
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" color="blue"><u>\1</u></a>', text)
    return text


def _inline_html(text: str) -> str:
    """Apply inline markdown → HTML."""
    from html import escape

    text = escape(text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Links (need to unescape the URL)
    def _link_replace(m):
        link_text = m.group(1)
        url = m.group(2).replace("&amp;", "&")
        return f'<a href="{url}">{link_text}</a>'

    text = re.sub(r"\[(.+?)\]\((.+?)\)", _link_replace, text)
    return text
