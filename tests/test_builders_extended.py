"""Tests for extended QMS builders: 8D, DOE run cards, supplier claim, knowledge health."""

from forgedoc import render
from forgedoc.builders.doe_run_cards import DOERunCards
from forgedoc.builders.eight_d import EightDReport
from forgedoc.builders.knowledge_health import KnowledgeHealthReport
from forgedoc.builders.supplier_claim import CoAMeasurement, SupplierClaimReport


class TestEightDReport:
    def test_basic_8d(self):
        report = EightDReport(
            title="8D: Supplier Defect",
            customer="Acme Motors",
            part_number="A-100",
        )
        report.d1_team = "Jane (lead), Bob (quality)"
        report.d2_problem = "Bore diameter OOT on 3 lots."
        report.d4_root_cause = "Tool wear not monitored."
        report.d5_corrective = "Implement SPC on bore op."

        doc = report.to_document()
        assert doc.title == "8D: Supplier Defect"
        assert len(doc.sections) == 8  # All 8 disciplines

    def test_8d_all_formats(self):
        report = EightDReport(title="Test 8D")
        report.d2_problem = "Test problem"
        doc = report.to_document()

        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"

        html = render(doc, format="html")
        assert "D2: Problem Description" in html

        docx = render(doc, format="docx")
        assert docx[:2] == b"PK"


class TestDOERunCards:
    def test_basic_doe(self):
        cards = DOERunCards(
            title="DOE: Viscosity x Feed Rate",
            factors=["Viscosity (cSt)", "Feed Rate (mm/min)"],
        )
        cards.add_run(1, [-1, -1], notes="Low baseline")
        cards.add_run(2, [+1, -1])
        cards.add_run(3, [-1, +1])
        cards.add_run(4, [+1, +1], notes="Both high")

        doc = cards.to_document()
        assert "DOE" in doc.subtitle
        assert len(cards.runs) == 4

    def test_doe_pdf(self):
        cards = DOERunCards(
            title="Test DOE",
            factors=["A", "B", "C"],
            response_names=["Surface Finish", "Dimensional"],
        )
        cards.add_run(1, [-1, -1, -1])
        cards.add_run(2, [+1, -1, -1])
        cards.add_run(3, [-1, +1, -1])
        cards.add_run(4, [+1, +1, +1])

        doc = cards.to_document()
        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"

    def test_doe_center_points(self):
        cards = DOERunCards(title="CCD", factors=["X", "Y"])
        cards.add_run(1, [0, 0], notes="Center point 1")
        cards.add_run(2, [0, 0], notes="Center point 2")
        doc = cards.to_document()
        html = render(doc, format="html")
        assert "Center (0)" in html

    def test_doe_full_factorial_3_factors(self):
        """Full 2^3 factorial — 8 runs."""
        cards = DOERunCards(
            title="2^3 Full Factorial",
            factors=["Temperature", "Pressure", "Time"],
            experimenter="Dr. Smith",
        )
        import itertools
        for i, levels in enumerate(itertools.product([-1, 1], repeat=3), 1):
            cards.add_run(i, list(levels))

        doc = cards.to_document()
        assert len(cards.runs) == 8
        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"


class TestSupplierClaimReport:
    def test_basic_claim(self):
        claim = SupplierClaimReport(
            title="Claim: OOT bore diameter",
            supplier="Apex Machining",
            part_number="A-100",
            severity="major",
        )
        claim.description = "Bore diameter out of tolerance."
        claim.add_measurement(CoAMeasurement(
            parameter="Bore ID",
            nominal=25.00,
            tolerance=0.02,
            measured=25.04,
            unit="mm",
            result="FAIL",
        ))
        claim.add_measurement(CoAMeasurement(
            parameter="OD",
            nominal=30.00,
            tolerance=0.05,
            measured=30.01,
            unit="mm",
            result="PASS",
        ))
        claim.supplier_response = "Tool wear identified."
        claim.corrective_action = "SPC implemented."
        claim.verification = "Next 3 lots: Cpk = 1.45."
        claim.disposition = "Return to supplier for rework."

        claim.to_document()
        assert len(claim.measurements) == 2

    def test_claim_all_formats(self):
        claim = SupplierClaimReport(title="Test Claim", supplier="Test Supplier")
        claim.description = "Test problem."
        claim.add_measurement(CoAMeasurement(
            parameter="Width", nominal=10.0, tolerance=0.1,
            measured=10.15, unit="mm", result="FAIL",
        ))
        doc = claim.to_document()

        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"

        html = render(doc, format="html")
        assert "Certificate of Analysis" in html

        docx = render(doc, format="docx")
        assert docx[:2] == b"PK"


class TestKnowledgeHealthReport:
    def test_basic_report(self):
        report = KnowledgeHealthReport(
            title="Knowledge Health: Q1 2026",
            organization="Acme Manufacturing",
            period="Q1 2026",
        )
        report.calibration_rate = 0.65
        report.staleness_rate = 0.12
        report.contradiction_rate = 0.03
        report.knowledge_gap_ratio = 0.35
        report.signal_velocity_days = 4.2
        report.proactive_ratio = 0.78

        report.add_maturity_level(1, True, "Structured knowledge exists")
        report.add_maturity_level(2, True, "Evidence accumulating")
        report.add_maturity_level(3, False, "Staleness above threshold")
        report.add_maturity_level(4, False, "No predictive validation yet")

        report.add_gap("CNC Line 3: coolant → surface finish (no evidence)")
        report.add_recommendation("Prioritize DOE on coolant parameters")

        report.to_document()
        assert len(report.maturity_levels) == 4
        assert len(report.gaps) == 1

    def test_health_report_with_trends(self):
        report = KnowledgeHealthReport(title="Trending")
        report.calibration_rate = 0.72
        report.prev_calibration_rate = 0.65
        report.staleness_rate = 0.08
        report.prev_staleness_rate = 0.12

        doc = report.to_document()
        html = render(doc, format="html")
        assert "Improving" in html

    def test_health_report_with_detection(self):
        report = KnowledgeHealthReport(title="Detection")
        report.detection_distribution = {"1": 2, "2": 5, "3": 8, "4": 12, "5": 3}

        doc = report.to_document()
        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"

    def test_health_report_all_formats(self):
        report = KnowledgeHealthReport(title="Full Report", organization="Test Corp")
        report.calibration_rate = 0.50
        report.add_maturity_level(1, True)
        report.add_gap("Test gap")
        report.add_recommendation("Test recommendation")
        doc = report.to_document()

        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"

        html = render(doc, format="html")
        assert "Test gap" in html

        docx = render(doc, format="docx")
        assert docx[:2] == b"PK"
