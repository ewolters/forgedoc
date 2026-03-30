"""Control Plan document — tabular, derived from process knowledge.

OLR-001: The control plan IS a view of the knowledge structure filtered
to "things we need to monitor in production." Each item traces to a
knowledge element (FMIS row / graph edge).

Usage:
    from forgedoc.builders.control_plan import ControlPlanDoc, ControlItem

    plan = ControlPlanDoc(
        title="Control Plan: CNC Machining Line 3",
        part_number="X-200",
        revision="B",
    )
    plan.add_item(ControlItem(
        process_step="Rough turning",
        characteristic="Surface finish Ra",
        specification="0.8 - 1.6 um",
        method="Profilometer",
        frequency="Every 5th part",
        reaction="Stop, notify supervisor, 100% sort",
        classification="critical",
    ))

    doc = plan.to_document()
    pdf = render(doc, format="pdf")
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core import Document, PageConfig, TableDef


@dataclass
class ControlItem:
    """A single control plan line item."""

    process_step: str
    characteristic: str
    specification: str
    method: str = ""
    frequency: str = ""
    sample_size: str = ""
    reaction: str = ""
    responsible: str = ""
    classification: str = "minor"  # critical, major, minor
    detection_level: int | None = None  # 1-8 per OLR-001 detection hierarchy
    knowledge_ref: str = ""  # FMIS row or graph edge reference


@dataclass
class ControlPlanDoc:
    """Control plan document builder."""

    title: str
    part_number: str = ""
    revision: str = ""
    process_name: str = ""
    prepared_by: str = ""
    date: str = ""
    items: list[ControlItem] = field(default_factory=list)

    def add_item(self, item: ControlItem) -> ControlItem:
        self.items.append(item)
        return item

    def to_document(self) -> Document:
        """Convert to a ForgeDoc Document."""
        doc = Document(
            title=self.title,
            subtitle="Control Plan",
            doc_type="control_plan",
            page_config=PageConfig(size="A3-landscape"),
            metadata={
                "Part Number": self.part_number,
                "Revision": self.revision,
                "Process": self.process_name,
                "Prepared By": self.prepared_by,
                "Date": self.date,
            },
        )

        # Summary counts
        critical = sum(1 for i in self.items if i.classification == "critical")
        major = sum(1 for i in self.items if i.classification == "major")
        minor = sum(1 for i in self.items if i.classification == "minor")

        summary = doc.add_section("Summary")
        summary.tables.append(TableDef(
            headers=["Classification", "Count"],
            rows=[
                ["Critical", str(critical)],
                ["Major", str(major)],
                ["Minor", str(minor)],
                ["Total", str(len(self.items))],
            ],
            style="compact",
        ))

        # Main control plan table
        sec = doc.add_section("Control Items")
        sec.tables.append(TableDef(
            headers=[
                "Step", "Characteristic", "Class.", "Spec",
                "Method", "Freq.", "Sample", "Reaction", "Owner", "Det. Level",
            ],
            rows=[
                [
                    item.process_step,
                    item.characteristic,
                    item.classification[0].upper(),  # C/M/m
                    item.specification,
                    item.method,
                    item.frequency,
                    item.sample_size,
                    item.reaction,
                    item.responsible,
                    str(item.detection_level) if item.detection_level else "—",
                ]
                for item in self.items
            ],
        ))

        return doc
