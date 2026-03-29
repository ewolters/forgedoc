"""A3 Problem Solving sheet — landscape A3, 8-section grid.

The A3 is a one-page thinking tool. Everything fits on one sheet.
Sections flow left-to-right, top-to-bottom following the PDCA cycle:

Left side (Plan):          Right side (Do/Check/Act):
  1. Background              5. Countermeasures
  2. Current Condition       6. Implementation Plan
  3. Goal / Target           7. Confirmation of Effect
  4. Root Cause Analysis     8. Follow-Up Actions

Usage:
    from forgedoc.builders.a3_sheet import A3Sheet

    a3 = A3Sheet(
        title="Nonconformance #4821",
        owner="Jane Smith",
        date="2026-03-29",
    )
    a3.background = "Customer reported dimensional variance on Part #X-200..."
    a3.current_condition = "Cpk = 0.87 on critical dimension (target: 1.33)..."
    a3.root_cause = "Coolant viscosity drop after 4hr run causes thermal expansion..."
    a3.countermeasures = "Install viscosity monitoring + automated coolant change..."

    doc = a3.to_document()
    pdf = render(doc, format="pdf")
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core import Document, PageConfig, Section


A3_SECTIONS = [
    ("background", "1. Background"),
    ("current_condition", "2. Current Condition"),
    ("goal", "3. Goal / Target"),
    ("root_cause", "4. Root Cause Analysis"),
    ("countermeasures", "5. Countermeasures"),
    ("implementation_plan", "6. Implementation Plan"),
    ("confirmation", "7. Confirmation of Effect"),
    ("follow_up", "8. Follow-Up Actions"),
]


@dataclass
class A3Sheet:
    """A3 problem solving document builder."""

    title: str
    owner: str = ""
    date: str = ""
    project: str = ""
    status: str = ""

    # Section content (plain text or markdown)
    background: str = ""
    current_condition: str = ""
    goal: str = ""
    root_cause: str = ""
    countermeasures: str = ""
    implementation_plan: str = ""
    confirmation: str = ""
    follow_up: str = ""

    def to_document(self) -> Document:
        """Convert to a ForgeDoc Document for rendering."""
        doc = Document(
            title=self.title,
            subtitle=f"A3 Problem Solving Report",
            doc_type="a3",
            page_config=PageConfig(size="A3-landscape"),
            metadata={
                "Owner": self.owner,
                "Date": self.date,
                "Project": self.project,
                "Status": self.status,
            },
        )

        for field_name, label in A3_SECTIONS:
            content = getattr(self, field_name, "") or ""
            doc.add_section(label, content, level=2)

        return doc
