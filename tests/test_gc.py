"""Tests for the garbage collection checks."""

import time
from pathlib import Path

import pytest
import yaml


# Import the internal functions directly
from harness_cli.commands.gc import (
    _check_doc_freshness,
    _check_orphaned_files,
    _check_constraint_consistency,
)


@pytest.fixture
def project(tmp_path):
    harness = tmp_path / ".harness"
    harness.mkdir()
    (harness / "constraints").mkdir()
    (harness / "context").mkdir()
    (tmp_path / "src").mkdir()
    return tmp_path


class TestDocFreshness:
    def test_recent_docs_no_issues(self, project):
        doc = project / ".harness" / "context" / "ARCH.md"
        doc.write_text("# Architecture")
        issues = _check_doc_freshness(project / ".harness", project)
        assert len(issues) == 0

    def test_no_context_dir(self, tmp_path):
        harness = tmp_path / ".harness"
        harness.mkdir()
        issues = _check_doc_freshness(harness, tmp_path)
        assert issues == []


class TestOrphanedFiles:
    def test_file_with_code_not_flagged(self, project):
        (project / "src" / "real.py").write_text("def hello(): pass")
        issues = _check_orphaned_files(project)
        assert len(issues) == 0

    def test_empty_file_flagged(self, project):
        (project / "src" / "empty.py").write_text("# just a comment\n")
        issues = _check_orphaned_files(project)
        assert len(issues) == 1
        assert issues[0]["type"] == "stale-artifact"

    def test_dunder_files_skipped(self, project):
        (project / "src" / "__init__.py").write_text("")
        issues = _check_orphaned_files(project)
        assert len(issues) == 0

    def test_no_src_dir(self, tmp_path):
        issues = _check_orphaned_files(tmp_path)
        assert issues == []


class TestConstraintConsistency:
    def test_valid_constraint_no_issues(self, project):
        constraint = {
            "name": "test",
            "description": "A test constraint",
            "severity": "error",
            "fix_message": "Fix it by doing X",
        }
        (project / ".harness" / "constraints" / "test.yml").write_text(
            yaml.dump(constraint)
        )
        issues = _check_constraint_consistency(project / ".harness", project)
        assert len(issues) == 0

    def test_missing_required_fields(self, project):
        (project / ".harness" / "constraints" / "bad.yml").write_text(
            yaml.dump({"name": "only-name"})
        )
        issues = _check_constraint_consistency(project / ".harness", project)
        field_issues = [i for i in issues if "Missing required field" in i["detail"]]
        assert len(field_issues) >= 2  # missing description and severity

    def test_missing_fix_message_warning(self, project):
        constraint = {
            "name": "no-fix",
            "description": "Has no fix message",
            "severity": "warning",
        }
        (project / ".harness" / "constraints" / "nofix.yml").write_text(
            yaml.dump(constraint)
        )
        issues = _check_constraint_consistency(project / ".harness", project)
        fix_issues = [i for i in issues if "fix_message" in i["detail"]]
        assert len(fix_issues) == 1
        assert fix_issues[0]["severity"] == "warning"

    def test_unparseable_yaml(self, project):
        (project / ".harness" / "constraints" / "broken.yml").write_text(": : :")
        issues = _check_constraint_consistency(project / ".harness", project)
        parse_issues = [i for i in issues if "Failed to parse" in i["detail"]]
        assert len(parse_issues) == 1
        assert parse_issues[0]["severity"] == "error"

    def test_empty_constraint_file(self, project):
        (project / ".harness" / "constraints" / "empty.yml").write_text("")
        issues = _check_constraint_consistency(project / ".harness", project)
        empty_issues = [i for i in issues if "Empty" in i["detail"]]
        assert len(empty_issues) == 1
