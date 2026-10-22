---
this_file: src_docs/md/current/tools/find-font-source-files.md
tags: ["Tools"]
categories: ["Tools"]
---

# Find Font Source Files

Find real font-source and script files in a chosen directory.

Setup: FontLab9/Python3.11, public Fly and App>=0.2.123.dev0.
Browse or type a directory, filename glob and optional literal text, then Find.
Decoded UTF8 replacement text; live filename glob; file symlinks included; progressively visible results and numeric KiB sizes; no Find-click history insertion.
Searches one directory without recursion. Progress and Cancel remain available;
repeat Find replaces the old query and closes its stream. Activate a result to
open its exact stored path through the desktop. No file is executed or changed.
The nonmodal owned window releases streams, iterators and timers on every close.
Practical font patterns replace the original generated sample directory.
Candidate collection is stepped to keep Cancel responsive; source iteration and
matching policy remain distinct. No application-wide event loop is started.
Historical source identifier: rescued/part2/ports/dialogs/pyqt-official/findfiles-63f2eeefd052f701.py; both original notices remain in NOTICE.

Run **Tools > Find Font Source Files** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7abb57ddfa749a13cba042dbda8f4abd95c2c7288674799b7a87ce12183804e4.py)
<!--/codeinclude-->
