"""Investigation Report — multi-page, evidence-driven.

OLR-001: An investigation produces knowledge. The compliance artifact
called "CAPA" is auto-assembled from investigation data. This builder
handles both the full investigation report and the CAPA compliance view.

Usage:
    from forgedoc.builders.investigation import InvestigationReport

    report = InvestigationReport(
        title="Investigation: Dimensional Variance on Part #X-200",
        signal_source="SPC alarm",
        severity="major",
    )
    report.add_scope("CNC machining center → surface finish → dimensional tolerance")
    report.add_evidence("DOE: Coolant viscosity vs surface finish", effect_size=0.34, p_value=0.002)
    report.add_root_cause("Coolant viscosity degrades after 4hr continuous run")
    report.add_corrective_action("Install inline viscosity monitoring", responsible="Maintenance", due="2026-04-15")
    report.add_verification("Process confirmation: 30-day monitoring shows Cpk = 1.45")

    doc = report.to_document()
    capa_doc = report.to_capa_document()  # Same data, CAPA format for auditors
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core import Document, Section, TableDef


@dataclass
class EvidenceRecord:
    """A piece of evidence from the investigation."""

    description: str
    source_type: str = ""  # doe, spc, observation, literature, gage_rr
    effect_size: float | None = None
    p_value: float | None = None
    confidence: str = ""  # high, medium, low
    date: str = ""


@dataclass
class CorrectiveAction:
    """An action to address the root cause."""

    description: str
    responsible: str = ""
    due: str = ""
    status: str = "open"


@dataclass
class InvestigationReport:
    """Investigation report builder."""

    title: str
    signal_source: str = ""
    severity: str = ""
    investigator: str = ""
    date_opened: str = ""
    date_closed: str = ""
    status: str = "open"

    scope: str = ""
    containment: str = ""
    root_causes: list[str] = field(default_factory=list)
    evidence: list[EvidenceRecord] = field(default_factory=list)
    corrective_actions: list[CorrectiveAction] = field(default_factory=list)
    verification: str = ""
    lessons_learned: str = ""

    def add_scope(self, scope: str):
        self.scope = scope

    def add_evidence(self, description: str, **kwargs) -> EvidenceRecord:
        rec = EvidenceRecord(description=description, **kwargs)
        self.evidence.append(rec)
        return rec

    def add_root_cause(self, cause: str):
        self.root_causes.append(cause)

    def add_corrective_action(self, description: str, **kwargs) -> CorrectiveAction:
        action = CorrectiveAction(description=description, **kwargs)
        self.corrective_actions.append(action)
        return action

    def to_document(self) -> Document:
        """Full investigation report."""
        doc = Document(
            title=self.title,
            subtitle="Investigation Report",
            doc_type="investigation",
            metadata={
                "Signal Source": self.signal_source,
                "Severity": self.severity,
                "Investigator": self.investigator,
                "Opened": self.date_opened,
                "Closed": self.date_closed or "In progress",
                "Status": self.status,
            },
        )

        if self.scope:
            doc.add_section("Scope", self.scope)

        if self.containment:
            doc.add_section("Containment Action", self.containment)

        # Evidence table
        if self.evidence:
            sec = doc.add_section("Evidence")
            sec.tables.append(TableDef(
                headers=["Description", "Source", "Effect Size", "p-value", "Confidence"],
                rows=[
                    [
                        e.description,
                        e.source_type,
                        f"{e.effect_size:.3f}" if e.effect_size is not None else "—",
                        f"{e.p_value:.4f}" if e.p_value is not None else "—",
                        e.confidence or "—",
                    ]
                    for e in self.evidence
                ],
            ))

        # Root causes
        if self.root_causes:
            doc.add_section(
                "Root Cause Analysis",
                "\n\n".join(f"{i+1}. {c}" for i, c in enumerate(self.root_causes)),
            )

        # Corrective actions table
        if self.corrective_actions:
            sec = doc.add_section("Corrective Actions")
            sec.tables.append(TableDef(
                headers=["Action", "Responsible", "Due", "Status"],
                rows=[
                    [a.description, a.responsible, a.due, a.status]
                    for a in self.corrective_actions
                ],
            ))

        if self.verification:
            doc.add_section("Verification", self.verification)

        if self.lessons_learned:
            doc.add_section("Lessons Learned", self.lessons_learned)

        return doc

    def to_capa_document(self) -> Document:
        """CAPA compliance view — same data, auditor-friendly format.

        OLR-001: CAPA is a VIEW on investigation data, not a separate process.
        """
        doc = Document(
            title=f"CAPA: {self.title}",
            subtitle="Corrective and Preventive Action Report (auto-generated from investigation)",
            doc_type="capa",
            metadata={
                "Source": self.signal_source,
                "Severity": self.severity,
                "Investigator": self.investigator,
                "Date Opened": self.date_opened,
                "Date Closed": self.date_closed or "Open",
            },
        )

        doc.add_section("1. Problem Description", self.scope or "(scope not defined)")
        doc.add_section("2. Containment", self.containment or "None documented")
        doc.add_section(
            "3. Root Cause",
            "\n\n".join(self.root_causes) if self.root_causes else "Investigation in progress",
        )

        if self.corrective_actions:
            sec = doc.add_section("4. Corrective Action")
            sec.tables.append(TableDef(
                headers=["Action", "Responsible", "Due", "Status"],
                rows=[[a.description, a.responsible, a.due, a.status] for a in self.corrective_actions],
            ))
        else:
            doc.add_section("4. Corrective Action", "Pending root cause analysis")

        doc.add_section("5. Preventive Action", self.lessons_learned or "Pending")
        doc.add_section("6. Verification of Effectiveness", self.verification or "Pending")

        if self.evidence:
            sec = doc.add_section("7. Supporting Evidence")
            sec.tables.append(TableDef(
                headers=["Evidence", "Type", "Result"],
                rows=[
                    [
                        e.description,
                        e.source_type,
                        f"ES={e.effect_size:.2f}, p={e.p_value:.3f}" if e.effect_size else e.confidence,
                    ]
                    for e in self.evidence
                ],
                style="compact",
            ))

        return doc
