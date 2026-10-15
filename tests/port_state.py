# this_file: tests/port_state.py
"""Gate only relocated catalogue states, never missing files or whole modules."""

import pytest


def require_current(record: dict) -> None:
    """Resume automatically when a record leaves the clean-room pending state."""
    if record["implementation"] == "clean_room_pending":
        pytest.skip(f"clean_room_pending: {record['source_id']}")


def require_all_current(records: list[dict]) -> None:
    """Gate an aggregate source assertion on the records it actually examines."""
    for record in records:
        require_current(record)
