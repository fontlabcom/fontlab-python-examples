---
this_file: src_docs/md/current/tools/font-reference-image-viewer-bounded-zoom.md
tags: ["Tools"]
categories: ["Tools"]
---

# Font Reference Image Viewer - Bounded Zoom

Inspect font reference artwork with the complete original image viewer.

Purpose:
    Examine scans, lettering samples and other local reference artwork while
    designing a font. Zoom, scroll, fit and print the image without editing it.
Setup:
    FontLab9, Python3.11, Fly and reviewed App>=0.2.156.dev0. No open font is
    required. Use FontLab's existing Qt runtime; install no alternate Qt binding.
Run:
    Open chooses a readable image. Cancel keeps the current view. Invalid files
    leave its image and zoom unchanged. Use View for zoom, Normal and Fit. Print
    opens an asynchronous owned printer dialog only on your explicit action.
Result:
    Zoom actions use the original thresholds and Fit exit resets to Normal. Printing fits the aspect ratio to the printer viewport. This profile writes only a PDF inside its owned temporary directory; closing removes that temporary output.
Compatibility:
    Close/Escape releases owned dialogs, painters and callbacks. Inputs and font
    data are unchanged. Native PythonQt/printer and whole-font acceptance remain
    pending. Original source: rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py

Run **Tools > Font Reference Image Viewer - Bounded Zoom** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a11ac1ee6145c9128eb9aeb763d7d5b87d56f577ca715fb38faad2c9def82ec8.py)
<!--/codeinclude-->
