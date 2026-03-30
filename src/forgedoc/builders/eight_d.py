"""8D Problem Solving Report.

The Eight Disciplines methodology — structured problem resolution
used in automotive (CQI), aerospace, and general manufacturing.

Usage:
    from forgedoc.builders.eight_d import EightDReport

    report = EightDReport(
        title="8D: Supplier Defect on Part #A-100",
        customer="Acme Motors",
        part_number="A-100",
    )
    report.d1_team = "Jane (lead), Bob (quality), Maria (engineering)"
    report.d2_problem = "Supplier parts OOT on bore diameter. 3 lots affected."
    report.d3_containment = "100% sort of incoming inventory. Notify customer."
    report.d4_root_cause = "Supplier tool wear not monitored. No SPC on bore op."
    report.d5_corrective = "Supplier to implement SPC. Tool change at 500 pieces."
    report.d6_verification = "First 3 lots after corrective: Cpk = 1.67."
    report.d7_prevention = "Add bore SPC to supplier PPAP requirements."
    report.d8_recognition = "Supplier quality team responded in 48hr."

    pdf = render(report.to_document(), format="pdf")
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core import Document

D8_SECTIONS = [
    ("d1_team", "D1: Team"),
    ("d2_problem", "D2: Problem Description"),
    ("d3_containment", "D3: Interim Containment Action"),
    ("d4_root_cause", "D4: Root Cause Analysis"),
    ("d5_corrective", "D5: Permanent Corrective Action"),
    ("d6_verification", "D6: Verification of Effectiveness"),
    ("d7_prevention", "D7: Systemic Prevention"),
    ("d8_recognition", "D8: Team Recognition"),
]


@dataclass
class EightDReport:
    """8D problem solving report builder."""

    title: str
    customer: str = ""
    part_number: str = ""
    report_number: str = ""
    date_opened: str = ""
    date_closed: str = ""
    status: str = "open"

    d1_team: str = ""
    d2_problem: str = ""
    d3_containment: str = ""
    d4_root_cause: str = ""
    d5_corrective: str = ""
    d6_verification: str = ""
    d7_prevention: str = ""
    d8_recognition: str = ""

    def to_document(self) -> Document:
        """Convert to a ForgeDoc Document."""
        doc = Document(
            title=self.title,
            subtitle="8D Problem Solving Report",
            doc_type="eight_d",
            metadata={
                "Customer": self.customer,
                "Part Number": self.part_number,
                "Report #": self.report_number,
                "Opened": self.date_opened,
                "Closed": self.date_closed or "In progress",
                "Status": self.status,
            },
        )

        for field_name, label in D8_SECTIONS:
            content = getattr(self, field_name, "") or ""
            doc.add_section(label, content or "*(pending)*", level=2)

        return doc
