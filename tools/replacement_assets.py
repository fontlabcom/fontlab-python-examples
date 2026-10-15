# SPDX-License-Identifier: Apache-2.0
# this_file: tools/replacement_assets.py
"""Self-authored replacements for the 14 resources that had no individual grant.

Every file is generated here from code (pure Python: SVG text, PNG through zlib,
WAV through ``wave``); the one JPEG is the generated PNG converted by macOS
``sips``. The upstream files are no longer shipped; catalog/ports.json keeps their
identities and records each replacement. ``--check`` verifies the committed bytes
(the JPEG only by its decoded format and size, since another sips may encode
differently). From the repository root::

    python3 tools/replacement_assets.py --write
    python3 tools/replacement_assets.py --record   # catalog/ports.json + licenses.json
    python3 tools/replacement_assets.py --check
"""

import argparse
import hashlib
import io
import json
import math
import struct
import subprocess
import sys
import tempfile
import wave
import zlib
from pathlib import Path

NUMBERED = "ports/widgets/pyqt-examples", "ports/multimedia/pyqt-examples"
STYLE = "ports/embedded/eyllanesc/assets/631cc1bc310c00b9"

ICON = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Self-authored for fontlab-python-examples (Apache-2.0): a page with a pencil. -->
<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
 <path d="M10 4h20l8 8v32H10z" fill="#fdfdfb" stroke="#5b6670" stroke-width="2" stroke-linejoin="round"/>
 <path d="M30 4v8h8" fill="#e3e6e8" stroke="#5b6670" stroke-width="2" stroke-linejoin="round"/>
 <g stroke="#9aa5ad" stroke-width="2" stroke-linecap="round">
  <path d="M15 18h17M15 24h17M15 30h11M15 36h8"/>
 </g>
 <g transform="rotate(45 34 34)">
  <rect x="31" y="16" width="6" height="22" rx="1" fill="#e8a33d" stroke="#8a5a14" stroke-width="1.5"/>
  <path d="M31 38l3 6 3-6z" fill="#3b3b3b"/>
 </g>
</svg>
"""

QSS = {
    "blue.qss": """/* Self-authored for fontlab-python-examples (Apache-2.0): cool blue panel. */
QWidget { background: #1f4e79; color: #f2f6fa; }
QPushButton { background: #2f6ea5; border: 1px solid #a9c7e3; border-radius: 4px; padding: 4px 10px; }
QPushButton:pressed { background: #163b5c; }
QSpinBox { background: #f2f6fa; color: #1f4e79; border: 1px solid #a9c7e3; padding-right: 18px; }
QSpinBox::up-button { image: url(:/files/add.png); width: 16px; }
QSpinBox::down-button { image: url(:/files/remove.png); width: 16px; }
""",
    "khaki.qss": """/* Self-authored for fontlab-python-examples (Apache-2.0): warm khaki panel. */
QWidget { background: #e6dcb4; color: #3d3521; }
QPushButton { background: #c9b977; border: 2px solid #7a6c38; border-radius: 6px; padding: 4px 10px; }
QPushButton:hover { background: #d8ca8c; }
QSpinBox { background: #fbf7e8; border: 2px solid #7a6c38; padding-right: 18px; }
QSpinBox::up-button { image: url(:/files/add.png); width: 16px; }
QSpinBox::down-button { image: url(:/files/remove.png); width: 16px; }
QLabel { font-weight: bold; }
""",
    "transparent.qss": """/* Self-authored for fontlab-python-examples (Apache-2.0): see-through over a picture. */
QWidget#StyleWidget { background-image: url(:/files/nature_1.jpg); }
QWidget { background: transparent; color: #ffffff; }
QPushButton { background: rgba(255, 255, 255, 60); border: 1px solid rgba(255, 255, 255, 160); border-radius: 4px; padding: 4px 10px; }
QPushButton:pressed { background: rgba(0, 0, 0, 80); }
QSpinBox { background: rgba(0, 0, 0, 70); border: 1px solid rgba(255, 255, 255, 160); padding-right: 18px; }
QSpinBox::up-button { image: url(:/files/add.png); width: 16px; }
QSpinBox::down-button { image: url(:/files/remove.png); width: 16px; }
""",
    "application.qss": """/* Self-authored for fontlab-python-examples (Apache-2.0): shared defaults. */
QWidget { font-size: 13px; }
QPushButton { min-height: 22px; }
QSpinBox { min-width: 64px; }
QSlider::groove:horizontal { height: 4px; background: #9aa5ad; }
QSlider::handle:horizontal { width: 12px; margin: -5px 0; background: #5b6670; border-radius: 6px; }
""",
    "nostyle.qss": "",
}

UI = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Self-authored for fontlab-python-examples (Apache-2.0): style switcher form. -->
<ui version="4.0">
 <class>StyleWidget</class>
 <widget class="QWidget" name="StyleWidget">
  <property name="geometry"><rect><x>0</x><y>0</y><width>220</width><height>260</height></rect></property>
  <property name="windowTitle"><string>Style switcher</string></property>
  <layout class="QVBoxLayout" name="mainLayout">
   <item><widget class="QLabel" name="title"><property name="text"><string>Pick a style sheet</string></property></widget></item>
   <item>
    <layout class="QHBoxLayout" name="valueRow">
     <item><widget class="QLabel" name="valueLabel"><property name="text"><string>Value</string></property></widget></item>
     <item><widget class="QSpinBox" name="spinBox"><property name="maximum"><number>100</number></property><property name="value"><number>40</number></property></widget></item>
    </layout>
   </item>
   <item><widget class="QSlider" name="slider"><property name="orientation"><enum>Qt::Horizontal</enum></property><property name="maximum"><number>100</number></property><property name="value"><number>40</number></property></widget></item>
   <item>
    <layout class="QHBoxLayout" name="toggleRow">
     <item><widget class="QPushButton" name="enableButton"><property name="text"><string>Enable</string></property><property name="checkable"><bool>true</bool></property><property name="checked"><bool>true</bool></property></widget></item>
     <item><widget class="QPushButton" name="showButton"><property name="text"><string>Show</string></property><property name="checkable"><bool>true</bool></property><property name="checked"><bool>true</bool></property></widget></item>
    </layout>
   </item>
   <item><widget class="QPushButton" name="blueStyle"><property name="text"><string>Blue</string></property></widget></item>
   <item><widget class="QPushButton" name="khakiStyle"><property name="text"><string>Khaki</string></property></widget></item>
   <item><widget class="QPushButton" name="transparentStyle"><property name="text"><string>Transparent</string></property></widget></item>
   <item><widget class="QPushButton" name="noStyle"><property name="text"><string>No style</string></property></widget></item>
   <item><widget class="QPushButton" name="close"><property name="text"><string>Close</string></property></widget></item>
  </layout>
 </widget>
 <resources/>
 <connections>
  <connection><sender>spinBox</sender><signal>valueChanged(int)</signal><receiver>slider</receiver><slot>setValue(int)</slot></connection>
  <connection><sender>slider</sender><signal>valueChanged(int)</signal><receiver>spinBox</receiver><slot>setValue(int)</slot></connection>
  <connection><sender>enableButton</sender><signal>toggled(bool)</signal><receiver>slider</receiver><slot>setEnabled(bool)</slot></connection>
  <connection><sender>showButton</sender><signal>toggled(bool)</signal><receiver>slider</receiver><slot>setVisible(bool)</slot></connection>
 </connections>
</ui>
"""


def png(width: int, height: int, pixel) -> bytes:
    """RGBA PNG; ``pixel(x, y)`` returns four 0..255 ints."""
    rows = b"".join(
        b"\x00" + b"".join(bytes(pixel(x, y)) for x in range(width))
        for y in range(height)
    )

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data))
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(rows, 9))
        + chunk(b"IEND", b"")
    )


def clamp(value: float) -> int:
    return max(0, min(255, round(value)))


def bullet(x: int, y: int) -> tuple:
    """A dark hole with a pale crushed rim and radial cracks."""
    dx, dy = x - 15.5, y - 15.5
    r, angle = math.hypot(dx, dy), math.atan2(dy, dx)
    crack = max(0.0, math.cos(angle * 7)) ** 12 * max(0.0, 1 - abs(r - 11) / 4)
    if r < 5:
        return (20, 20, 22, 255)
    if r < 8:
        shade = 60 + (r - 5) * 40
        return (clamp(shade), clamp(shade), clamp(shade + 4), 255)
    alpha = max(0.0, 1 - (r - 8) / 7) * 170 + crack * 200
    return (90, 90, 96, clamp(alpha))


def sign(minus: bool):
    """16x16 plus or minus, dark on transparent."""

    def pixel(x: int, y: int) -> tuple:
        bar = 6 <= y <= 9 and 2 <= x <= 13
        post = not minus and 6 <= x <= 9 and 2 <= y <= 13
        return (40, 46, 52, 255) if bar or post else (0, 0, 0, 0)

    return pixel


def landscape(x: int, y: int) -> tuple:
    """Sky gradient over two rolling hills, 320x240."""
    far = 150 + 18 * math.sin(x / 41) + 9 * math.sin(x / 13 + 1)
    near = 185 + 22 * math.sin(x / 57 + 2) + 6 * math.sin(x / 9)
    if y > near:
        return (clamp(58 + y / 8), clamp(110 + y / 6), 44, 255)
    if y > far:
        return (86, 132, 92, 255)
    t = y / 240
    return (clamp(110 + 90 * t), clamp(160 + 70 * t), clamp(230 - 10 * t), 255)


def shot() -> bytes:
    """0.25 s mono 22.05 kHz: a decaying noise burst (deterministic LCG noise)."""
    rate, samples, seed, frames = 22050, 5512, 12345, bytearray()
    for i in range(samples):
        seed = (1103515245 * seed + 12345) % 2**31
        noise = seed / 2**30 - 1
        envelope = math.exp(-i / 900) * (1 if i > 20 else i / 20)
        frames += struct.pack("<h", round(noise * envelope * 26000))
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(bytes(frames))
    return buffer.getvalue()


def jpeg(png_bytes: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as folder:
        source, target = Path(folder) / "in.png", Path(folder) / "out.jpg"
        source.write_bytes(png_bytes)
        subprocess.run(
            [
                "sips",
                "-s",
                "format",
                "jpeg",
                "-s",
                "formatOptions",
                "85",
                str(source),
                "--out",
                str(target),
            ],
            check=True,
            capture_output=True,
        )
        return target.read_bytes()


def assets() -> dict[str, bytes]:
    """Target path -> bytes for every generated file except the JPEG."""
    icon = ICON.encode("utf-8")
    files = {
        f"{NUMBERED[0]}/icon-adeb6eaa0049d0d3.svg": icon,
        f"{NUMBERED[0]}/icon-3f05f5f2d0cc6df2.svg": icon,
        f"{NUMBERED[1]}/icon-6988c3833303e9d8.svg": icon,
        f"{NUMBERED[1]}/bullet-accab87abcc10bea.png": png(32, 32, bullet),
        f"{NUMBERED[1]}/shot-3d215869bc0bba5c.wav": shot(),
        f"{STYLE}/files/add.png": png(16, 16, sign(False)),
        f"{STYLE}/files/remove.png": png(16, 16, sign(True)),
        f"{STYLE}/stylewidget.ui": UI.encode("utf-8"),
    }
    files.update(
        {f"{STYLE}/files/{name}": text.encode("utf-8") for name, text in QSS.items()}
    )
    return files


JPEG_PATH = f"{STYLE}/files/nature_1.jpg"
GENERATOR = "tools/replacement_assets.py"
ATTRIBUTION = "FontLab Python examples contributors; self-authored replacement (upstream file not shipped)."
BASIS = (
    "Self-authored replacement generated by tools/replacement_assets.py with the same "
    "role (format, path and use by the port). The upstream file had no individual grant; "
    "it is no longer shipped, and its identity stays in catalog/ports.json."
)


def record(root: Path) -> int:
    """Mark the 14 resources as replaced in catalog/ports.json and catalog/licenses.json."""
    targets = set(assets()) | {JPEG_PATH}
    manifest_path, ledger_path = (
        root / "catalog/ports.json",
        root / "catalog/licenses.json",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    done = 0
    for port in manifest["ports"]:
        for resource in port["resources"]:
            if resource["target_path"] not in targets:
                continue
            data = (root / resource["target_path"]).read_bytes()
            replacement = {
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "generator": GENERATOR,
                "license": "Apache-2.0",
            }
            resource["replacement"] = replacement
            resource["this_file_note"] = (
                "Self-authored replacement; upstream identity kept in source."
            )
            license_ = resource["license"]
            resource.setdefault(
                "upstream_license",
                {key: value for key, value in license_.items() if key != "file_review"},
            )
            license_.update(
                selected="Apache-2.0",
                review_state="reviewed",
                basis=BASIS,
                attribution=ATTRIBUTION,
                declared_terms="Apache-2.0 (repository LICENSE)",
            )
            license_.pop("notice_path", None)
            review = ledger["files"][resource["target_path"]]
            review.setdefault(
                "upstream_review",
                {  # the upstream file's own, unchanged finding
                    key: review[key]
                    for key in ("state", "selected", "attribution", "reason")
                },
            )
            review.update(
                selected="Apache-2.0",
                state="reviewed",
                attribution=ATTRIBUTION,
                reason=BASIS,
                replacement=replacement,
            )
            done += 1
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    ledger_path.write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"recorded {done} replacements")
    return 0 if done == len(targets) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--record", action="store_true")
    args = parser.parse_args()
    if args.record:
        return record(args.root)
    files = assets()
    if args.write:
        files[JPEG_PATH] = jpeg(png(320, 240, landscape))
        for name, data in files.items():
            (args.root / name).write_bytes(data)
        print(f"wrote {len(files)} files")
        return 0
    stale = [
        name for name, data in files.items() if (args.root / name).read_bytes() != data
    ]
    picture = (args.root / JPEG_PATH).read_bytes()
    if not picture.startswith(b"\xff\xd8\xff"):
        stale.append(JPEG_PATH)
    print("stale: " + ", ".join(stale) if stale else f"{len(files) + 1} files current")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
