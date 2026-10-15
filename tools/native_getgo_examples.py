# this_file: tools/native_getgo_examples.py
"""Run the examples/getgo scripts inside FontLab and check their documented results.

Go through the workspace guard (the mutating examples need a no-document session):

    fl-native.sh --mutating --lane E1-getgo-native -- \
        uv run --project fontlab-remopy python tools/native_getgo_examples.py \
        --output DIR --fonttools-site SITE_PACKAGES [--ids font_audit ...]

Each entry runs from a QTimer callback, not inside ``run_python`` (whose 5 s deadline
would abort long exports and opens). The host polls a receipt dict. Per example the
receipt keeps the result, the manifest's expectations (``examples.getgo._checks``),
timing, document state before/after, and the unchanged-fixture check.
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples/getgo/native_manifest.json"
FIXTURES = ROOT / "testdata/getgo"

ARM = '''
import builtins, sys, time, traceback, json
from PythonQt import QtCore

state = {"done": False, "error": None, "result": None, "checked": False, "seconds": None}
builtins._e1_example = state

def finish():
    start = time.time()
    saved = sys.path[:]
    try:
        sys.path[:0] = [root]
        sys.path.extend(p for p in extra_paths if p not in sys.path)
        for key in [k for k in sys.modules if k == "examples" or k.startswith("examples.")]:
            del sys.modules[key]
        import importlib
        module = importlib.import_module(module_name)
        assert module.__file__.startswith(root + "/"), module.__file__
        from examples.getgo._checks import assert_expected
        result = getattr(module, entry)(**kwargs)
        try:
            assert_expected(result, expected)
            state["checked"] = True
        finally:
            state["result"] = json.loads(json.dumps(
                result if isinstance(result, (dict, list)) else getattr(result, "report", repr(result)),
                default=repr))
            if cleanup == "handle.close":
                result.close()
                QtCore.QCoreApplication.processEvents()
    except BaseException:
        state["error"] = traceback.format_exc()
    finally:
        sys.path[:] = saved
        for key in [k for k in sys.modules if k == "examples" or k.startswith("examples.")]:
            del sys.modules[key]
        state["seconds"] = round(time.time() - start, 2)
        state["done"] = True

builtins._e1_example_cb = finish
QtCore.QTimer.singleShot(0, finish)
result = True
'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_example(fl, example: dict, extra_paths: list[str], limit: float) -> dict:
    """Run one manifest entry; failures are data."""
    record = {"id": example["id"], "fonts": example["fonts"], "mutates": example["mutates_owned_copy"]}
    before = [f["id"] for f in fl.fonts()]
    record["documents_before"] = len(before)
    try:
        fl.run(ARM, root=str(ROOT), extra_paths=extra_paths, module_name=example["module"],
               entry=example["entry_function"], kwargs=example["kwargs"], expected=example["expected"],
               cleanup=example["cleanup_function"])
        start = time.time()
        while time.time() - start < limit:
            state = fl.run("import builtins\nresult = dict(builtins._e1_example)").value
            if state["done"]:
                break
            time.sleep(0.5)
        else:
            raise TimeoutError(f"example still running after {limit} s")
        record.update(state)
        record["passed"] = bool(state["checked"] and not state["error"])
    except Exception as error:
        record.update(passed=False, error=f"{type(error).__name__}: {error}")
    # An aborted or timed-out example may leave its owned copy open (modified): close what it opened.
    # Wait out a still-running callback first so the close cannot race it.
    stray = [f["id"] for f in fl.fonts() if f["id"] not in before]
    for ident in stray:
        try:
            fl.close_font(font_id=ident, save=False)
        except Exception as error:
            record.setdefault("cleanup_errors", []).append(f"{type(error).__name__}: {error}")
    record["closed_stray_documents"] = len(stray)
    record["documents_after"] = len(fl.fonts())
    record["no_documents_left"] = record["documents_after"] == record["documents_before"]
    return record


def main() -> int:
    from fontlab_remopy import FontLab

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fonttools-site", required=True, type=Path, help="site-packages providing fontTools for FontLab")
    parser.add_argument("--ids", nargs="*")
    parser.add_argument("--timeout", type=float, default=120)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    examples = [e for e in manifest["examples"] if not args.ids or e["id"] in args.ids]
    if args.ids and {e["id"] for e in examples} != set(args.ids):
        parser.error("unknown example id")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    receipt = output / "receipt.json"
    if receipt.exists():
        parser.error("choose a new evidence directory")
    rows = {r["id"]: r for r in json.loads((FIXTURES / "manifest.json").read_text())["fonts"]}
    report = {"manifest_sha256": sha256(MANIFEST), "requested": [e["id"] for e in examples], "results": []}
    with FontLab(timeout=args.timeout) as fl:
        assert not fl.fonts(), "requires a no-document session"
        for example in examples:
            record = run_example(fl, example, [str(args.fonttools_site.resolve())], args.timeout)
            record["fixtures_unchanged"] = all(
                sha256(FIXTURES / rows[f]["path"]) == rows[f]["sha256"] for f in example["fonts"])
            report["results"].append(record)
            receipt.write_text(json.dumps(report, indent=2) + "\n")
            print(example["id"], "PASS" if record["passed"] else (record.get("error") or "FAIL").strip().splitlines()[-1],
                  flush=True)
            if not (record["no_documents_left"] and record["fixtures_unchanged"]):
                print("host state uncertain; stopping", file=sys.stderr)
                break
    report["passed"] = len(report["results"]) == len(examples) and all(
        r["passed"] and r["no_documents_left"] and r["fixtures_unchanged"] for r in report["results"])
    receipt.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
