---
this_file: src_docs/md/current/widgets/script-icon-browser.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Script Icon Browser

What: Browse the standard icons supplied by FontLab's current Qt style.
How: Enumerate QStyle SP_ constants, filter their names and show each icon
beside its enum name. A selected row produces pasteable PythonQt code.
Why: Use icons already supplied by the host instead of bundling image assets.
Usage: Filter by a name such as Dialog or Dir. Preview, then select an icon.
Copy the code below into a FontLab script. These are Qt standard icons;
FontLab's private resource icons are outside this browser.
Benefit: Build consistent script panels without external icon dependencies.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only tool.
App owns panel lifetime, signals and completion.
Independent rewrite of the Qt Icons example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.

Run **Widgets > Script Icon Browser** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `7904e8816b86027e0a4c18237d8eb1fc3d91743825540527e1b63268f7646deb`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Widgets/Script%20Icon%20Browser.py)
