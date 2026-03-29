"""Tests for QMS document builders."""

from forgedoc import render
from forgedoc.builders.a3_sheet import A3Sheet
from forgedoc.builders.investigation import InvestigationReport
from forgedoc.builders.control_plan import ControlPlanDoc, ControlItem


class TestA3Sheet:
    def test_basic_a3(self):
        a3 = A3Sheet(
            title="Nonconformance #4821",
            owner="Jane Smith",
            date="2026-03-29",
        )
        a3.background = "Customer reported dimensional variance."
        a3.root_cause = "Coolant viscosity drop after 4hr run."
        a3.countermeasures = "Install viscosity monitoring."

        doc = a3.to_document()
        assert doc.title == "Nonconformance #4821"
        assert doc.page_config.size == "A3-landscape"
        assert len(doc.sections) == 8  # All 8 A3 sections

    def test_a3_renders_pdf(self):
        a3 = A3Sheet(title="Test A3")
        a3.background = "Test background."
        doc = a3.to_document()
        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"

    def test_a3_renders_html(self):
        a3 = A3Sheet(title="Test A3")
        a3.goal = "Reduce defect rate by 50%."
        doc = a3.to_document()
        html = render(doc, format="html")
        assert "Reduce defect rate" in html


class TestInvestigationReport:
    def test_basic_investigation(self):
        report = InvestigationReport(
            title="Dimensional Variance Investigation",
            signal_source="SPC alarm",
            severity="major",
        )
        report.add_scope("CNC machining → surface finish")
        report.add_evidence("DOE: viscosity vs finish", effect_size=0.34, p_value=0.002)
        report.add_root_cause("Coolant degrades after 4hr")
        report.add_corrective_action("Install monitoring", responsible="Maintenance", due="2026-04-15")
        report.verification = "30-day Cpk = 1.45"

        doc = report.to_document()
        assert doc.title == "Dimensional Variance Investigation"
        assert len(report.evidence) == 1
        assert len(report.corrective_actions) == 1

    def test_investigation_pdf(self):
        report = InvestigationReport(title="Test Investigation")
        report.add_root_cause("Test cause")
        doc = report.to_document()
        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"

    def test_capa_view(self):
        """CAPA is a VIEW on investigation data, not a separate document."""
        report = InvestigationReport(
            title="Test Investigation",
            signal_source="customer complaint",
        )
        report.add_scope("Assembly line defect")
        report.add_root_cause("Operator training gap")
        report.add_corrective_action("Retrain team", responsible="HR")

        capa = report.to_capa_document()
        assert capa.title.startswith("CAPA:")
        assert capa.doc_type == "capa"

        # CAPA sections follow the standard format
        section_titles = [s.title for s in capa.sections]
        assert "1. Problem Description" in section_titles
        assert "3. Root Cause" in section_titles
        assert "4. Corrective Action" in section_titles

    def test_capa_pdf(self):
        report = InvestigationReport(title="CAPA Test")
        report.add_root_cause("Root cause")
        report.add_corrective_action("Fix it")
        capa = report.to_capa_document()
        pdf = render(capa, format="pdf")
        assert pdf[:5] == b"%PDF-"


class TestControlPlan:
    def test_basic_control_plan(self):
        plan = ControlPlanDoc(
            title="Control Plan: Line 3",
            part_number="X-200",
            revision="B",
        )
        plan.add_item(ControlItem(
            process_step="Rough turning",
            characteristic="Surface finish Ra",
            specification="0.8 - 1.6 um",
            method="Profilometer",
            frequency="Every 5th part",
            reaction="Stop, sort",
            classification="critical",
            detection_level=4,
        ))
        plan.add_item(ControlItem(
            process_step="Finish turning",
            characteristic="OD dimension",
            specification="25.00 +/- 0.02 mm",
            method="CMM",
            frequency="First/last + hourly",
            classification="major",
        ))

        doc = plan.to_document()
        assert doc.page_config.size == "A3-landscape"
        assert len(plan.items) == 2

    def test_control_plan_pdf(self):
        plan = ControlPlanDoc(title="Test Plan")
        plan.add_item(ControlItem(
            process_step="Step 1",
            characteristic="Dim A",
            specification="10 +/- 0.1",
        ))
        doc = plan.to_document()
        pdf = render(doc, format="pdf")
        assert pdf[:5] == b"%PDF-"
