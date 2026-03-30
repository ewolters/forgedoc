"""ForgeDoc — opinionated document builder for quality management systems.

Usage:
    from forgedoc import Document, render

    doc = Document(title="Investigation #4821")
    doc.add_section("Problem Statement", "Nonconformance detected on Line 3...")
    doc.add_table(headers=["Cause", "Evidence", "Confidence"], rows=data)
    pdf_bytes = render(doc, format="pdf")

QMS-specific builders:
    from forgedoc.builders.a3_sheet import A3Sheet
    from forgedoc.builders.control_plan import ControlPlanDoc
    from forgedoc.builders.investigation import InvestigationReport
"""

__version__ = "0.1.0"

from .core import Branding, Document, render

__all__ = ["Branding", "Document", "render", "__version__"]
