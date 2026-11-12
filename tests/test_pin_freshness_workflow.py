# this_file: tests/test_pin_freshness_workflow.py
"""The public CI workflow must run the Scriptmix pin checks read-only, with only the App-tab skip allowed."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/pin-freshness.yml"


def text() -> str:
    assert WORKFLOW.is_file(), "missing .github/workflows/pin-freshness.yml"
    return WORKFLOW.read_text()


def test_workflow_when_read_then_checks_out_public_scriptmix_without_credentials():
    body = text()
    assert "repository: fontlabcom/fontlab-python-scriptmix" in body
    assert "persist-credentials: false" in body
    assert "FONTLAB_SCRIPTMIX_ROOT: ${{ github.workspace }}/_scriptmix" in body
    assert "fetch-depth: 0" in body, "the removal-commit history check needs full Scriptmix history"


def test_workflow_when_read_then_runs_both_pin_test_files():
    body = text()
    assert "tests/test_scriptmix_pin_freshness.py" in body
    assert "tests/test_scriptmix_destinations.py" in body


def test_workflow_when_read_then_only_app_tab_skips_are_tolerated():
    body = text()
    assert "FONTLAB_EXAMPLES_SKIP_APP_TAB:" in body
    assert "App tab check skipped" in body, "the skip filter must name the only allowed skip"
    assert "SKIPPED" in body


def test_workflow_when_read_then_is_read_only_and_never_deploys():
    body = text()
    assert "permissions:\n  contents: read" in body
    for forbidden in ("pages:", "deploy", "contents: write", "secrets.", "id-token"):
        assert forbidden not in body, f"pin-freshness workflow must not use {forbidden!r}"


def test_workflow_when_read_then_actions_are_pinned_to_full_shas():
    uses = [line.split("uses:", 1)[1].strip() for line in text().splitlines() if "uses:" in line]
    assert uses, "workflow has no actions"
    for ref in uses:
        sha = ref.split("@", 1)[1].split()[0]
        assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha), f"unpinned action: {ref}"


def test_workflow_when_read_then_runs_weekly_on_a_schedule():
    body = text()
    assert "  schedule:\n    - cron: '" in body, "a weekly schedule trigger catches Scriptmix drift without an Examples push"
    cron = body.split("- cron: '", 1)[1].split("'", 1)[0].split()
    assert len(cron) == 5 and cron[2:] == ["*", "*", cron[4]] and cron[4].isdigit(), "cron must fire once a week"
