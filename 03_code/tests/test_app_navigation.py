"""Regression tests for deferred dashboard navigation."""

from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import (  # noqa: E402
    apply_pending_navigation_before_widgets,
    initialize_dashboard_state,
    schedule_navigation,
    select_completed_run,
)


def test_completed_run_selection_schedules_without_late_indicator_mutation():
    state = {}
    initialize_dashboard_state(state)
    state["_active_completed_run"] = "old"
    state["selected_indicator"] = "far"
    assert select_completed_run(state, "new")
    assert state["selected_indicator"] == "far"
    assert state["_pending_selected_run"] == "new"


def test_pending_navigation_is_one_shot_and_resets_selected_cell():
    state = {}
    initialize_dashboard_state(state)
    state["selected_cell_id"] = "old_cell"
    schedule_navigation(state, "new", "gsi")
    assert apply_pending_navigation_before_widgets(state)
    assert state["selected_completed_run"] == "new"
    assert state["selected_indicator"] == "gsi"
    assert state["selected_cell_id"] is None
    assert not apply_pending_navigation_before_widgets(state)
