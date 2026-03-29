"""DOE Run Instruction Cards.

Formatted cards for technicians running designed experiments.
Each card shows one experimental run with factor settings.

Usage:
    from forgedoc.builders.doe_run_cards import DOERunCards

    cards = DOERunCards(
        title="DOE: Coolant Viscosity × Feed Rate",
        factors=["Viscosity (cSt)", "Feed Rate (mm/min)", "Depth of Cut (mm)"],
    )
    cards.add_run(1, [-1, -1, -1], notes="Low settings baseline")
    cards.add_run(2, [+1, -1, -1], notes="High viscosity only")
    cards.add_run(3, [-1, +1, -1])
    cards.add_run(4, [+1, +1, +1], notes="All high — check for interaction")

    pdf = render(cards.to_document(), format="pdf")
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core import Document, Section, TableDef


@dataclass
class RunCard:
    """A single experimental run."""

    run_number: int
    factor_levels: list[float]
    notes: str = ""
    response_fields: list[str] | None = None  # What to measure


@dataclass
class DOERunCards:
    """DOE run instruction cards builder."""

    title: str
    factors: list[str] = field(default_factory=list)
    response_names: list[str] = field(default_factory=lambda: ["Response"])
    runs: list[RunCard] = field(default_factory=list)
    experimenter: str = ""
    date: str = ""
    randomize: bool = True

    def add_run(self, run_number: int, factor_levels: list[float], notes: str = "") -> RunCard:
        card = RunCard(
            run_number=run_number,
            factor_levels=factor_levels,
            notes=notes,
        )
        self.runs.append(card)
        return card

    def to_document(self) -> Document:
        """Convert to a ForgeDoc Document.

        Produces a summary table followed by individual run cards.
        """
        doc = Document(
            title=self.title,
            subtitle="DOE Run Instruction Cards",
            doc_type="doe_run_cards",
            metadata={
                "Experimenter": self.experimenter,
                "Date": self.date,
                "Factors": ", ".join(self.factors),
                "Total Runs": str(len(self.runs)),
                "Randomized": "Yes" if self.randomize else "No (standard order)",
            },
        )

        # Summary table — all runs at a glance
        summary = doc.add_section("Run Summary")
        headers = ["Run #"] + self.factors + ["Notes"]
        rows = []
        for run in self.runs:
            level_strs = [_format_level(lv) for lv in run.factor_levels]
            rows.append([str(run.run_number)] + level_strs + [run.notes])
        summary.tables.append(TableDef(headers=headers, rows=rows))

        # Individual run cards
        cards_section = doc.add_section("Run Cards")
        for run in self.runs:
            card = Section(
                title=f"Run {run.run_number}",
                level=3,
            )
            # Factor settings table
            factor_rows = []
            for i, factor in enumerate(self.factors):
                level = run.factor_levels[i] if i < len(run.factor_levels) else 0
                factor_rows.append([factor, _format_level(level)])
            card.tables.append(TableDef(
                headers=["Factor", "Setting"],
                rows=factor_rows,
                style="compact",
            ))

            # Response recording table
            response_rows = [[name, "________"] for name in self.response_names]
            card.tables.append(TableDef(
                headers=["Response", "Measured Value"],
                rows=response_rows,
                style="compact",
                caption="Record measured values during this run",
            ))

            if run.notes:
                card.content = f"**Notes:** {run.notes}"

            cards_section.subsections.append(card)

        return doc


def _format_level(level: float) -> str:
    """Format a factor level for display."""
    if level == -1:
        return "Low (−1)"
    elif level == 1 or level == +1:
        return "High (+1)"
    elif level == 0:
        return "Center (0)"
    else:
        return f"{level:+.2f}"
