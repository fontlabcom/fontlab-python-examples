# this_file: Scripts/Widgets/Font Units Calculator.py
# SPDX-License-Identifier: Apache-2.0
"""What: Calculate font-unit values and their em and point equivalents.
How: Read the current font UPM on each Calculate. Apply one explicit operation.
Why: Keep unit arithmetic separate from stored glyph metrics.
Usage: Enter A, an operation and B. Set the proof size in points. Calculate,
then select and copy the result. No expression evaluation or font writes.
Benefit: Transfer measured values into spacing and proof-size decisions.

Original profile setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only tool.
App owns panel lifetime, signals and completion.
Independent rewrite of the Qt Calculator example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Metrics Controls Lab; opens the Font Units Calculator profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E03", profile='Font Units Calculator')


if __name__ == "__main__":
    main()
