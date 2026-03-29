# ForgeDoc

Opinionated document builder for quality management systems. Renders structured data to PDF (ReportLab), DOCX (python-docx), and HTML (pure Python).

## What This Is

A standalone Python package — no Django, no web framework dependency. Build documents programmatically, render to any format.

**Generic core:** `Document`, `Section`, `Table`, `Branding` → `render(doc, format="pdf")`

**QMS builders** (optional, `pip install forgedoc[qms]`):
- `A3Sheet` — landscape A3, 8-section PDCA grid
- `InvestigationReport` — multi-page evidence-driven report + CAPA compliance view
- `ControlPlanDoc` — tabular control plan with classification tiers

## Architecture

```
forgedoc/
├── core.py          # Document, Section, TableDef, Branding, render()
├── renderers/
│   ├── pdf.py       # ReportLab platypus
│   ├── docx.py      # python-docx
│   └── html.py      # Pure Python, no deps
├── styles/
│   └── default.py   # Colors, fonts, table styles
└── builders/        # QMS-specific document types
    ├── a3_sheet.py
    ├── investigation.py
    └── control_plan.py
```

## Usage

```python
from forgedoc import Document, render

doc = Document(title="Report", subtitle="Q1 Review")
doc.add_section("Summary", "Production met targets across all lines.")
doc.add_table(headers=["Metric", "Target", "Actual"], rows=[["OEE", "85%", "87.2%"]])
pdf_bytes = render(doc, format="pdf")
```

## Running Tests

```bash
pip install -e ".[qms,dev]"
pytest tests/ -v
```

## Integration with SVEND

SVEND uses ForgeDoc via a thin `documents/` Django app that:
1. Assemblers fetch data from Django models + verify auth
2. Build ForgeDoc Documents using builders
3. Render via `forgedoc.render()`
4. Return HTTP response or queue via Tempora

ForgeDoc itself knows nothing about Django, SVEND, or databases.

## License

MIT
