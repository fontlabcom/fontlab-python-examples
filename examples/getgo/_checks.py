# SPDX-License-Identifier: Apache-2.0
# this_file: examples/getgo/_checks.py
"""Small, explicit native-result assertions used by native_manifest.json."""


def result_value(result, path: list):
    """Resolve dict/list entries or the UI handle's documented attributes."""
    for key in path:
        result = (
            result[key]
            if isinstance(result, (dict, list, tuple))
            else getattr(result, key)
        )
    return result


def assert_expected(result, checks: list[dict]) -> None:
    """Support only the four assertion forms documented in the manifest."""
    for check in checks:
        value = result_value(result, check["path"])
        rule, expected = next(
            (key, value) for key, value in check.items() if key != "path"
        )
        if rule == "equals":
            ok = value == expected
        elif rule == "len":
            ok = len(value) == expected
        elif rule == "contains":
            ok = expected in value
        elif rule == "gt":
            ok = value > expected
        else:
            raise ValueError(f"Unknown GetGo expectation: {rule}")
        if not ok:
            raise AssertionError(
                f"GetGo result {check['path']}: {rule} {expected!r}; got {value!r}"
            )
