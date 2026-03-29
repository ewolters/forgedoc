"""Supplier Claim Report.

Documents the lifecycle of a supplier quality claim: initial report,
CoA data, response, and verification results.

Usage:
    from forgedoc.builders.supplier_claim import SupplierClaimReport, CoAMeasurement

    claim = SupplierClaimReport(
        title="Claim #SC-042: OOT bore diameter on Part A-100",
        supplier="Apex Machining Inc.",
        part_number="A-100",
        severity="major",
    )
    claim.description = "Incoming inspection found bore diameter OOT on lot #L-2026-03."
    claim.add_measurement(CoAMeasurement(
        parameter="Bore ID", nominal=25.00, tolerance=0.02,
        measured=25.04, unit="mm", result="FAIL",
    ))
    claim.supplier_response = "Tool wear identified. Replaced insert at op 30."
    claim.corrective_action = "SPC on bore op, tool change at 500pc interval."
    claim.verification = "Next 3 lots all within spec. Cpk = 1.45."

    pdf = render(claim.to_document(), format="pdf")
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core import Document, Section, TableDef


@dataclass
class CoAMeasurement:
    """A single measurement from a Certificate of Analysis."""

    parameter: str
    nominal: float | None = None
    tolerance: float | None = None
    measured: float | None = None
    unit: str = ""
    result: str = ""  # PASS/FAIL


@dataclass
class SupplierClaimReport:
    """Supplier quality claim report builder."""

    title: str
    supplier: str = ""
    part_number: str = ""
    lot_number: str = ""
    claim_number: str = ""
    severity: str = ""
    date_opened: str = ""
    date_closed: str = ""
    status: str = "open"

    description: str = ""
    containment: str = ""
    measurements: list[CoAMeasurement] = field(default_factory=list)
    supplier_response: str = ""
    corrective_action: str = ""
    verification: str = ""
    disposition: str = ""  # rework, scrap, use-as-is, return

    def add_measurement(self, m: CoAMeasurement) -> CoAMeasurement:
        self.measurements.append(m)
        return m

    def to_document(self) -> Document:
        """Convert to a ForgeDoc Document."""
        doc = Document(
            title=self.title,
            subtitle="Supplier Quality Claim Report",
            doc_type="supplier_claim",
            metadata={
                "Supplier": self.supplier,
                "Part Number": self.part_number,
                "Lot": self.lot_number,
                "Claim #": self.claim_number,
                "Severity": self.severity,
                "Opened": self.date_opened,
                "Closed": self.date_closed or "In progress",
                "Status": self.status,
            },
        )

        doc.add_section("Problem Description", self.description or "*(pending)*")

        if self.containment:
            doc.add_section("Containment Action", self.containment)

        # CoA measurements table
        if self.measurements:
            sec = doc.add_section("Certificate of Analysis — Measurements")
            sec.tables.append(TableDef(
                headers=["Parameter", "Nominal", "Tol.", "Measured", "Unit", "Result"],
                rows=[
                    [
                        m.parameter,
                        f"{m.nominal:.3f}" if m.nominal is not None else "—",
                        f"\u00b1{m.tolerance:.3f}" if m.tolerance is not None else "—",
                        f"{m.measured:.3f}" if m.measured is not None else "—",
                        m.unit,
                        m.result,
                    ]
                    for m in self.measurements
                ],
            ))

        if self.supplier_response:
            doc.add_section("Supplier Response", self.supplier_response)

        if self.corrective_action:
            doc.add_section("Corrective Action", self.corrective_action)

        if self.verification:
            doc.add_section("Verification of Effectiveness", self.verification)

        if self.disposition:
            doc.add_section("Lot Disposition", self.disposition)

        return doc
