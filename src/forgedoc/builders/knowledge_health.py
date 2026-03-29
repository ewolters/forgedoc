"""Knowledge Health Report — management review input.

OLR-001: The quarterly management review is replaced by continuous
visibility into process knowledge state. This report is a snapshot
of that state for leadership decision-making.

Usage:
    from forgedoc.builders.knowledge_health import KnowledgeHealthReport

    report = KnowledgeHealthReport(
        title="Knowledge Health: Q1 2026",
        organization="Acme Manufacturing",
    )
    report.calibration_rate = 0.65
    report.staleness_rate = 0.12
    report.contradiction_rate = 0.03
    report.knowledge_gap_ratio = 0.35
    report.signal_velocity_days = 4.2
    report.proactive_ratio = 0.78

    report.add_maturity_level(1, True, "Structured knowledge exists")
    report.add_maturity_level(2, True, "Evidence accumulating")
    report.add_maturity_level(3, False, "Staleness rate above threshold (12% > 10%)")

    report.add_gap("CNC Line 3: coolant system → surface finish (no evidence)")
    report.add_gap("Assembly: torque spec → joint integrity (assertion only since Jan)")

    report.add_recommendation("Prioritize DOE on CNC coolant parameters")
    report.add_recommendation("Schedule process confirmation on assembly torque")

    pdf = render(report.to_document(), format="pdf")
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core import Document, Section, TableDef


@dataclass
class MaturityLevel:
    """A maturity level assessment."""

    level: int
    achieved: bool
    detail: str = ""


@dataclass
class KnowledgeHealthReport:
    """Knowledge health snapshot for management review."""

    title: str
    organization: str = ""
    report_date: str = ""
    period: str = ""  # "Q1 2026", "March 2026", etc.
    prepared_by: str = ""

    # Core metrics (0.0 - 1.0)
    calibration_rate: float | None = None
    staleness_rate: float | None = None
    contradiction_rate: float | None = None
    knowledge_gap_ratio: float | None = None
    signal_velocity_days: float | None = None
    proactive_ratio: float | None = None

    # Detection distribution
    detection_distribution: dict[str, int] = field(default_factory=dict)

    # Maturity assessment
    maturity_levels: list[MaturityLevel] = field(default_factory=list)

    # Gaps and recommendations
    gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Trends (optional — previous period values for comparison)
    prev_calibration_rate: float | None = None
    prev_staleness_rate: float | None = None

    def add_maturity_level(self, level: int, achieved: bool, detail: str = ""):
        self.maturity_levels.append(MaturityLevel(level, achieved, detail))

    def add_gap(self, description: str):
        self.gaps.append(description)

    def add_recommendation(self, description: str):
        self.recommendations.append(description)

    def to_document(self) -> Document:
        """Convert to a ForgeDoc Document."""
        doc = Document(
            title=self.title,
            subtitle="Process Knowledge Health Report",
            doc_type="knowledge_health",
            metadata={
                "Organization": self.organization,
                "Report Date": self.report_date,
                "Period": self.period,
                "Prepared By": self.prepared_by,
            },
        )

        # Key metrics table
        sec = doc.add_section("Knowledge Health Metrics")
        metrics_rows = []
        if self.calibration_rate is not None:
            trend = _trend(self.calibration_rate, self.prev_calibration_rate)
            metrics_rows.append([
                "Calibration Rate",
                f"{self.calibration_rate:.0%}",
                "Edges with empirical evidence / total edges",
                trend,
            ])
        if self.staleness_rate is not None:
            trend = _trend_inverse(self.staleness_rate, self.prev_staleness_rate)
            metrics_rows.append([
                "Staleness Rate",
                f"{self.staleness_rate:.0%}",
                "Calibrated edges past review threshold / calibrated total",
                trend,
            ])
        if self.contradiction_rate is not None:
            metrics_rows.append([
                "Contradiction Rate",
                f"{self.contradiction_rate:.0%}",
                "Edges with conflicting evidence / total",
                "",
            ])
        if self.knowledge_gap_ratio is not None:
            metrics_rows.append([
                "Knowledge Gap",
                f"{self.knowledge_gap_ratio:.0%}",
                "Assertion-only edges / total (no empirical evidence)",
                "",
            ])
        if self.signal_velocity_days is not None:
            metrics_rows.append([
                "Signal Resolution",
                f"{self.signal_velocity_days:.1f} days",
                "Average time from signal to knowledge update",
                "",
            ])
        if self.proactive_ratio is not None:
            metrics_rows.append([
                "Proactive Detection",
                f"{self.proactive_ratio:.0%}",
                "Internal detection / total (vs customer-reported)",
                "",
            ])

        if metrics_rows:
            sec.tables.append(TableDef(
                headers=["Metric", "Value", "Definition", "Trend"],
                rows=metrics_rows,
            ))

        # Detection distribution
        if self.detection_distribution:
            det_sec = doc.add_section("Detection Mechanism Distribution", level=2)
            det_rows = [
                [f"Level {k}", str(v)]
                for k, v in sorted(self.detection_distribution.items())
            ]
            det_sec.tables.append(TableDef(
                headers=["Detection Level", "Critical Node Count"],
                rows=det_rows,
                style="compact",
            ))

        # Maturity assessment
        if self.maturity_levels:
            mat_sec = doc.add_section("Maturity Assessment")
            mat_rows = [
                [
                    f"Level {m.level}",
                    _MATURITY_NAMES.get(m.level, ""),
                    "Achieved" if m.achieved else "Not achieved",
                    m.detail,
                ]
                for m in self.maturity_levels
            ]
            mat_sec.tables.append(TableDef(
                headers=["Level", "Name", "Status", "Detail"],
                rows=mat_rows,
            ))

        # Knowledge gaps
        if self.gaps:
            doc.add_section(
                "Priority Knowledge Gaps",
                "\n\n".join(f"- {g}" for g in self.gaps),
            )

        # Recommendations
        if self.recommendations:
            doc.add_section(
                "Recommendations",
                "\n\n".join(f"- {r}" for r in self.recommendations),
            )

        return doc


_MATURITY_NAMES = {
    1: "Structured",
    2: "Learning",
    3: "Sustaining",
    4: "Predictive",
}


def _trend(current: float, previous: float | None) -> str:
    if previous is None:
        return ""
    diff = current - previous
    if abs(diff) < 0.005:
        return "Stable"
    return f"{'Improving' if diff > 0 else 'Declining'} ({diff:+.0%})"


def _trend_inverse(current: float, previous: float | None) -> str:
    """For metrics where lower is better."""
    if previous is None:
        return ""
    diff = current - previous
    if abs(diff) < 0.005:
        return "Stable"
    return f"{'Improving' if diff < 0 else 'Declining'} ({diff:+.0%})"
