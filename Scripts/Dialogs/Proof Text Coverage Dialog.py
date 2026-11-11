# this_file: Scripts/Dialogs/Proof Text Coverage Dialog.py
# SPDX-License-Identifier: Apache-2.0
"""Check proof text against current-font Unicode assignments.

Original profile setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Click Enter Proof Text to open a modeless standard input dialog. Accept to inspect coverage; Cancel keeps the existing draft. Preview reads the current font again. Duplicate assignments remain visible.
Why: Use a modeless text dialog and normalize Qt UTF-16 text.
Benefit: Find missing characters and ambiguous assignments before proofing.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank standarddialogs dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
The author supplies these first-party samples under Apache-2.0.
The Qt examples carry BSD headers and collection-level GPL metadata.
No code, helper or asset from these examples is included.
The two archived variants consolidate into this FontLab-specific workflow.
Historical source: rescued/part2/ports/dialogs/pyqt-official/standarddialogs-e1a0a829f8f2e311.py
SHA256: 4a705367140cd7600706cf7ab7522523ddc7c5cd3592309c78d316b67cfc0055
Historical source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/standarddialogs-e1a0a829f8f2e311.py
SHA256: 80b66bcc88b46955f88d0b31040a2ea4cdf272aa6de1f825c9ff189abf21af22


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Unicode Lab; opens the Proof Text Coverage Dialog profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E08", profile='Proof Text Coverage Dialog')


if __name__ == "__main__":
    main()
