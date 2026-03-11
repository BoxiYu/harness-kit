"""Tests for the Loop Detector engine."""

import time
from pathlib import Path

import pytest

from harness_cli.engine.loop_detector import LoopDetector


@pytest.fixture
def detector(tmp_path):
    """Create a detector with a short time window for testing."""
    return LoopDetector(tmp_path, edit_threshold=3, time_window=60)


class TestRecordAndCheck:
    def test_single_edit_no_loop(self, detector):
        detector.record_edit("src/foo.py")
        result = detector.check("src/foo.py")
        assert not result.is_loop
        assert result.edit_count == 1

    def test_below_threshold_no_loop(self, detector):
        detector.record_edit("src/foo.py")
        detector.record_edit("src/foo.py")
        result = detector.check("src/foo.py")
        assert not result.is_loop
        assert result.edit_count == 2

    def test_at_threshold_triggers_loop(self, detector):
        for _ in range(3):
            detector.record_edit("src/foo.py")
        result = detector.check("src/foo.py")
        assert result.is_loop
        assert result.edit_count == 3

    def test_above_threshold_still_loop(self, detector):
        for _ in range(5):
            detector.record_edit("src/foo.py")
        result = detector.check("src/foo.py")
        assert result.is_loop
        assert result.edit_count == 5

    def test_different_files_independent(self, detector):
        for _ in range(3):
            detector.record_edit("src/foo.py")
        detector.record_edit("src/bar.py")

        assert detector.check("src/foo.py").is_loop
        assert not detector.check("src/bar.py").is_loop

    def test_untracked_file_no_loop(self, detector):
        result = detector.check("src/never_edited.py")
        assert not result.is_loop
        assert result.edit_count == 0


class TestInterventionMessage:
    def test_loop_has_intervention_message(self, detector):
        for _ in range(3):
            detector.record_edit("src/foo.py")
        result = detector.check("src/foo.py")
        assert "LOOP ADVISORY" in result.intervention_message
        assert "src/foo.py" in result.intervention_message

    def test_no_loop_no_message(self, detector):
        detector.record_edit("src/foo.py")
        result = detector.check("src/foo.py")
        assert result.intervention_message == ""

    def test_context_in_message(self, detector):
        detector.record_edit("src/foo.py", context="adding auth")
        detector.record_edit("src/foo.py", context="fixing import")
        detector.record_edit("src/foo.py", context="trying again")
        result = detector.check("src/foo.py")
        assert "adding auth" in result.intervention_message
        assert "fixing import" in result.intervention_message
        assert "trying again" in result.intervention_message

    def test_duplicate_contexts_deduped(self, detector):
        detector.record_edit("src/foo.py", context="same thing")
        detector.record_edit("src/foo.py", context="same thing")
        detector.record_edit("src/foo.py", context="same thing")
        result = detector.check("src/foo.py")
        # Should appear only once in the message
        assert result.intervention_message.count("same thing") == 1


class TestTimeWindow:
    def test_old_edits_outside_window(self, detector):
        # Manually inject old events
        old_time = time.time() - 120  # 2 minutes ago (within 60s window? no)
        # Actually window is 60s, so 120s ago is outside
        detector.events = []
        from harness_cli.engine.loop_detector import EditEvent
        for _ in range(3):
            detector.events.append(EditEvent(
                file="src/foo.py",
                timestamp=old_time,
            ))
        result = detector.check("src/foo.py")
        assert not result.is_loop

    def test_recent_edits_inside_window(self, detector):
        now = time.time()
        from harness_cli.engine.loop_detector import EditEvent
        for _ in range(3):
            detector.events.append(EditEvent(
                file="src/foo.py",
                timestamp=now - 10,  # 10 seconds ago, within 60s window
            ))
        result = detector.check("src/foo.py")
        assert result.is_loop


class TestPersistence:
    def test_save_and_load(self, tmp_path):
        d1 = LoopDetector(tmp_path, edit_threshold=3, time_window=60)
        d1.record_edit("src/foo.py", context="first")
        d1.record_edit("src/foo.py", context="second")
        d1.save()

        d2 = LoopDetector.load(tmp_path, edit_threshold=3, time_window=60)
        assert len(d2.events) == 2
        assert d2.events[0].file == "src/foo.py"
        assert d2.events[0].context == "first"

    def test_load_missing_file(self, tmp_path):
        d = LoopDetector.load(tmp_path)
        assert d.events == []

    def test_load_corrupt_file(self, tmp_path):
        state_file = tmp_path / ".harness" / "state" / "loop-detector.json"
        state_file.parent.mkdir(parents=True)
        state_file.write_text("not json", encoding="utf-8")
        d = LoopDetector.load(tmp_path)
        assert d.events == []


class TestClear:
    def test_clear_specific_file(self, detector):
        detector.record_edit("src/foo.py")
        detector.record_edit("src/bar.py")
        detector.clear("src/foo.py")
        assert len([e for e in detector.events if e.file == "src/foo.py"]) == 0
        assert len([e for e in detector.events if e.file == "src/bar.py"]) == 1

    def test_clear_all(self, detector):
        detector.record_edit("src/foo.py")
        detector.record_edit("src/bar.py")
        detector.clear()
        assert detector.events == []


class TestCheckAll:
    def test_check_all_returns_multi_edit_files(self, detector):
        detector.record_edit("src/foo.py")
        detector.record_edit("src/foo.py")
        detector.record_edit("src/bar.py")

        results = detector.check_all()
        files = [r.file for r in results]
        assert "src/foo.py" in files
        assert "src/bar.py" not in files  # only 1 edit

    def test_check_all_empty(self, detector):
        assert detector.check_all() == []
