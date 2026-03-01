"""
Tests for Developer 3's scorecard and analytics service.
"""

import pytest
from services.watchtower.scorecard_service import assign_scorecard_color
from shared.enums import SeverityColor


class TestAssignScorecardColor:
    """Tests for department scorecard color assignment."""

    def test_low_score_is_yellow(self):
        assert assign_scorecard_color(20.0) == SeverityColor.YELLOW.value

    def test_medium_score_is_orange(self):
        assert assign_scorecard_color(50.0) == SeverityColor.ORANGE.value

    def test_high_score_is_red(self):
        assert assign_scorecard_color(80.0) == SeverityColor.RED.value

    def test_zero_score_is_yellow(self):
        assert assign_scorecard_color(0.0) == SeverityColor.YELLOW.value

    def test_boundary_40_is_orange(self):
        assert assign_scorecard_color(40.0) == SeverityColor.ORANGE.value

    def test_boundary_70_is_red(self):
        assert assign_scorecard_color(70.0) == SeverityColor.RED.value
