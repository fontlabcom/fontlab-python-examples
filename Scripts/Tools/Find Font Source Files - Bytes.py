# this_file: Scripts/Tools/Find Font Source Files - Bytes.py
# SPDX-License-Identifier: Apache-2.0
"""Find real font-source and script files in a chosen directory.

Setup: FontLab9/Python3.11, public Fly and App>=0.2.123.dev0.
Browse or type a directory, filename glob and optional literal text, then Find.
Exact UTF8 byte matching; captured blank-or-glob; file symlinks excluded; final table only; unique Find-click histories; literal KB sizes.
Searches one directory without recursion. Progress and Cancel remain available;
repeat Find replaces the old query and closes its stream. Activate a result to
open its exact stored path through the desktop. No file is executed or changed.
The nonmodal owned window releases streams, iterators and timers on every close.
Practical font patterns replace the original generated sample directory.
Candidate collection is stepped to keep Cancel responsive; source iteration and
matching policy remain distinct. No application-wide event loop is started.
Native PythonQt and desktop/file-dialog lifecycle qualification remain pending.
Historical source identifier: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/findfiles-63f2eeefd052f701.py; both original notices remain in NOTICE.
"""


def main() -> None:
    """Open the complete paired workflow through the lazy public Fly facade."""
    from fly.ap.find_files import show_bytes

    show_bytes()


if __name__ == "__main__":
    main()
