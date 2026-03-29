# ForgeDoc

Opinionated document builder for quality management systems. Turns structured data into professional PDF, DOCX, and HTML documents with zero system dependencies.

## Install

```bash
pip install forgedoc          # Core (PDF + HTML)
pip install forgedoc[docx]    # Add DOCX support
pip install forgedoc[qms]     # Add QMS document builders
```

## Quick Start

```python
from forgedoc import Document, render

doc = Document(title="Monthly Review", subtitle="March 2026")
doc.add_section("Summary", "Production exceeded targets across all lines.")
doc.add_table(
    headers=["Metric", "Target", "Actual", "Status"],
    rows=[
        ["OEE", "85%", "87.2%", "Met"],
        ["Scrap Rate", "<2%", "1.4%", "Met"],
        ["On-Time Delivery", "95%", "93.1%", "Miss"],
    ],
)
doc.add_section("Actions", "Investigate delivery shortfall on Line 3.")

pdf_bytes = render(doc, format="pdf")
html_str = render(doc, format="html")
docx_bytes = render(doc, format="docx")
```

## QMS Builders

Pre-built document types for quality management:

### A3 Problem Solving

```python
from forgedoc.builders.a3_sheet import A3Sheet

a3 = A3Sheet(
    title="Dimensional Variance on Part #X-200",
    owner="Jane Smith",
    date="2026-03-29",
)
a3.background = "Customer reported OOT condition on critical dimension."
a3.current_condition = "Cpk = 0.87 (target: 1.33). 12 rejects in 500-piece run."
a3.root_cause = "Coolant viscosity degrades after 4-hour continuous run."
a3.countermeasures = "Inline viscosity monitor + automated coolant change at threshold."
a3.confirmation = "30-day monitoring: Cpk = 1.45, zero rejects."

pdf = render(a3.to_document(), format="pdf")
```

### Investigation Report + CAPA View

```python
from forgedoc.builders.investigation import InvestigationReport

report = InvestigationReport(
    title="Investigation: Surface Finish Nonconformance",
    signal_source="SPC alarm",
    severity="major",
)
report.add_scope("CNC machining center → surface finish → dimensional tolerance")
report.add_evidence("DOE: Coolant viscosity vs surface finish",
                    effect_size=0.34, p_value=0.002, source_type="doe")
report.add_root_cause("Coolant viscosity degrades after 4hr continuous run")
report.add_corrective_action("Install inline viscosity monitoring",
                             responsible="Maintenance", due="2026-04-15")
report.verification = "Process confirmation: 30-day monitoring shows Cpk = 1.45"

# Full investigation report
pdf = render(report.to_document(), format="pdf")

# CAPA compliance view — same data, auditor-friendly format
capa_pdf = render(report.to_capa_document(), format="pdf")
```

### Control Plan

```python
from forgedoc.builders.control_plan import ControlPlanDoc, ControlItem

plan = ControlPlanDoc(
    title="Control Plan: CNC Machining Line 3",
    part_number="X-200",
    revision="B",
)
plan.add_item(ControlItem(
    process_step="Rough turning",
    characteristic="Surface finish Ra",
    specification="0.8 - 1.6 μm",
    method="Profilometer",
    frequency="Every 5th part",
    reaction="Stop, notify supervisor, 100% sort",
    classification="critical",
    detection_level=4,
))

pdf = render(plan.to_document(), format="pdf")
```

## Branding

```python
from forgedoc import Document, render
from forgedoc.core import Branding

doc = Document(
    title="Quarterly Review",
    branding=Branding(
        company_name="Acme Manufacturing",
        logo_path="/path/to/logo.png",
        accent_color="#2d5f8a",
        footer_text="Confidential — Acme Manufacturing Inc.",
    ),
)
```

## Custom Styles

```python
from forgedoc.styles.default import StyleConfig

custom = StyleConfig(
    primary_color="#2d5f8a",
    accent_color="#1a4a6e",
    font_family="Helvetica",
    heading_size=16,
    body_size=10,
)

pdf = render(doc, format="pdf", style=custom)
```

## Architecture

ForgeDoc is framework-agnostic. No Django, Flask, or web framework required.

```
Document (data)  →  Renderer (engine)  →  Output (bytes/str)
     ↑                    ↑
  Builders            ReportLab (PDF)
  (QMS types)         python-docx (DOCX)
                      Pure Python (HTML)
```

- **Document**: Dataclass tree (title, sections, tables, metadata, branding)
- **Builders**: Opinionated constructors for specific document types
- **Renderers**: Format-specific output engines
- **Styles**: Configurable colors, fonts, spacing, table formatting

## Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| reportlab | PDF rendering | Yes (core) |
| python-docx | DOCX rendering | Optional (`[docx]`) |

Zero system-level dependencies. No cairo, no pango, no wkhtmltopdf. `pip install` and go.

## License

MIT
