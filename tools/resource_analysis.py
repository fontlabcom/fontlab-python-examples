# this_file: tools/resource_analysis.py
"""Extract XML/QML structure and observable capability needs without Qt."""

import re
import xml.etree.ElementTree as ET
from pathlib import PurePosixPath


def resource_analysis(path: str, text: str) -> dict:
    suffix = PurePosixPath(path).suffix
    if suffix == ".qml":
        return {
            "qml": {
                "imports": re.findall(r"(?m)^\s*import\s+([^\n]+)", text),
                "references": sorted(
                    set(
                        re.findall(
                            r'["\']([^"\'\n]+\.(?:png|jpg|svg|qml|ttf|wav|mp4))["\']',
                            text,
                        )
                    )
                ),
            }
        }
    if suffix not in {".ui", ".qrc"}:
        return {}
    try:
        root = ET.fromstring(text)
        return {
            "xml": {
                "state": "parsed",
                "classes": sorted(
                    {e.attrib["class"] for e in root.iter() if "class" in e.attrib}
                ),
                "references": sorted(
                    {e.text.strip() for e in root.iter("file") if e.text}
                ),
            }
        }
    except ET.ParseError:
        return {"xml": {"state": "parse-error", "classes": [], "references": []}}


def capabilities(path: str, text: str, analysis: dict) -> list[str]:
    """Observable needs, not assertions of host availability."""
    code = (
        "\n".join(
            line for line in text.splitlines() if not line.lstrip().startswith("#")
        )
        if PurePosixPath(path).suffix in {".py", ".qml", ".ui", ".qrc", ".js", ".html"}
        else ""
    )
    haystack = path.lower() + " " + code.lower()
    rules = {
        "qml": (".qml", "qtqml", "qtquick", "qqml"),
        "webengine": ("webengine",),
        "multimedia": ("qtmultimedia", "qmediaplayer", "qaudio", "qvideo"),
        "gstreamer": ("gst-pipeline", "gst_pipeline", "gi.repository"),
        "matplotlib": ("matplotlib", "backend_qt"),
        "database": ("qtsql", "qsql", "sqlite", "/sql/", "database"),
        "network": (
            "qtnetwork",
            "qnetwork",
            "websocket",
            "requests",
            "http://",
            "https://",
        ),
        "platform": (
            "activeqt",
            "qax",
            "dbus",
            "serialport",
            "positioning",
            "win32",
            "xvimagesink",
            "v4l2src",
        ),
        "graphics-painting": ("qpainter", "qgraphics", "opengl", "qtsvg"),
        "video-overlay": (
            "not_classified/1",
            "qabstractvideosurface",
            "qmlvideoviewer",
        ),
        "designer-ui": (".ui", "uic.", "qtuitools"),
        "threads-processes": ("qthread", "qprocess", "threading", "multiprocessing"),
    }
    needs = {
        name for name, needles in rules.items() if any(n in haystack for n in needles)
    }
    if analysis.get("qt_bindings"):
        needs.add("qt-binding-adaptation")
    if any(
        "QApplication" in c or c.endswith((".exec", ".exec_"))
        for c in analysis.get("api_calls", [])
    ):
        needs.add("host-event-loop-adaptation")
    return sorted(needs)
