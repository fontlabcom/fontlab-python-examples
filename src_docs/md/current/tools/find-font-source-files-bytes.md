---
this_file: src_docs/md/current/tools/find-font-source-files-bytes.md
tags: ["Tools"]
categories: ["Tools"]
---

# Find Font Source Files - Bytes

Find real font-source and script files in a chosen directory.

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
Historical source identifier: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/findfiles-63f2eeefd052f701.py; both original notices remain in NOTICE.

Run **Tools > Find Font Source Files - Bytes** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d71118bffbf523644131ce19cc21f3cdc8544cc67ae46be7c4efd7600becec67.py)
<!--/codeinclude-->
