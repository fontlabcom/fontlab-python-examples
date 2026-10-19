# this_file: lessons/src/fontlab_python_lessons/getgo/_checks.py
# SPDX-License-Identifier: Apache-2.0
"""Small, explicit native-result assertions used by native_manifest.json."""

from typing import Any


def result_value(result: Any, path: list) -> Any:
    """Resolve dict/list entries or the UI handle's documented attributes."""
    for key in path:
        result = result[key] if isinstance(result, (dict, list, tuple)) else getattr(result, key)
    return result


def assert_expected(result: Any, checks: list[dict]) -> None:
    """Support only the four assertion forms documented in the manifest."""
    for check in checks:
        value = result_value(result, check["path"])
        rule, expected = next((key, value) for key, value in check.items() if key != "path")
        if rule == "equals":
            ok = value == expected
        elif rule == "len":
            ok = len(value) == expected
        elif rule == "contains":
            ok = expected in value
        elif rule == "gt":
            ok = value > expected
        else:
            msg = f"Unknown GetGo expectation: {rule}"
            raise ValueError(msg)
        if not ok:
            msg = f"GetGo result {check['path']}: {rule} {expected!r}; got {value!r}"
            raise AssertionError(
                msg,
            )
