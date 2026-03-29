"""HTML renderer — pure Python, no dependencies beyond stdlib.

Produces self-contained HTML with inline CSS. No Django, no Jinja2.
Useful for previews, email bodies, or as input to other tools.
"""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Document


def render_html(doc: Document, **kwargs) -> str:
    """Render a Document to a self-contained HTML string."""
    parts = [_HTML_HEAD.format(title=escape(doc.title))]

    # Header
    if doc.branding.company_name:
        parts.append(f'<div class="company">{escape(doc.branding.company_name)}</div>')
    parts.append(f"<h1>{escape(doc.title)}</h1>")
    if doc.subtitle:
        parts.append(f'<p class="subtitle">{escape(doc.subtitle)}</p>')

    # Metadata
    if doc.metadata:
        parts.append('<table class="meta">')
        for k, v in doc.metadata.items():
            if v:
                parts.append(f"<tr><td><strong>{escape(str(k))}</strong></td>"
                             f"<td>{escape(str(v))}</td></tr>")
        parts.append("</table>")

    # Sections
    for section in doc.sections:
        parts.append(_render_section_html(section))

    parts.append("</body></html>")
    return "\n".join(parts)


def _render_section_html(section) -> str:
    """Render a section to HTML."""
    parts = []
    if section.title:
        tag = f"h{min(section.level + 1, 4)}"
        parts.append(f"<{tag}>{escape(section.title)}</{tag}>")

    if section.content:
        for para in section.content.split("\n\n"):
            para = para.strip()
            if para:
                parts.append(f"<p>{escape(para)}</p>")

    for table_def in section.tables:
        parts.append("<table>")
        parts.append("<thead><tr>")
        for h in table_def.headers:
            parts.append(f"<th>{escape(str(h))}</th>")
        parts.append("</tr></thead><tbody>")
        for row in table_def.rows:
            parts.append("<tr>")
            for cell in row:
                parts.append(f"<td>{escape(str(cell))}</td>")
            parts.append("</tr>")
        parts.append("</tbody></table>")
        if table_def.caption:
            parts.append(f'<p class="caption">{escape(table_def.caption)}</p>')

    for sub in section.subsections:
        parts.append(_render_section_html(sub))

    return "\n".join(parts)


_HTML_HEAD = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 2em auto; color: #1a1a1a; font-size: 14px; line-height: 1.5; }}
h1 {{ color: #1a1a2e; border-bottom: 2px solid #1a1a2e; padding-bottom: 0.3em; }}
h2 {{ color: #16213e; margin-top: 1.5em; }}
h3 {{ color: #16213e; }}
.company {{ color: #666; font-size: 0.9em; }}
.subtitle {{ color: #666; font-size: 1.1em; margin-top: -0.5em; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th {{ background: #1a1a2e; color: white; text-align: left; padding: 6px 8px; font-size: 0.85em; }}
td {{ padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 0.85em; }}
tr:nth-child(even) {{ background: #fafafa; }}
.meta td {{ border: none; padding: 2px 12px 2px 0; font-size: 0.9em; }}
.caption {{ font-size: 0.8em; color: #666; text-align: center; }}
</style></head><body>"""
