# this_file: Scripts/Graphics/Glyph Review Cards.py
# SPDX-License-Identifier: Apache-2.0
"""What: Stage glyph review status and notes on a graphics canvas.
How: Embed one native form per matching glyph. Status and notes stay local.
Why: Review comments need a scratch space beside a font before handoff.
Usage: Enter a prefix that matches at most six names, then Refresh. Set each
status and note. Copy Result transfers the complete report to the clipboard.
Copy before Refresh or Close; Discard and Close explicitly drops local notes.
Benefit: Prepare a named review handoff without altering glyph notes or history.
Notes are plain text. Unsupported Qt text classes are refused during transfer.

Original profile setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; no font writes.
Independent rewrite of the Qt embeddeddialogs example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Historical source: rescued/part2/ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py
SHA256: c08d4c310c70b3a0e129085b79f59493472859819fdf1c75e7024345724a83bc
Historical source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py
SHA256: b90e385b1cb4ea7f2f202545920844cba59a825fcdf3986878ebd25d3fce1876


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Review Model Lab; opens the Glyph Review Cards profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E09", profile='Glyph Review Cards')


if __name__ == "__main__":
    main()
