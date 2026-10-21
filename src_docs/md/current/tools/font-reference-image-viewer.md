---
this_file: src_docs/md/current/tools/font-reference-image-viewer.md
tags: ["Tools"]
categories: ["Tools"]
---

# Font Reference Image Viewer

Inspect font reference artwork with the complete original image viewer.

Purpose:
    Examine scans, lettering samples and other local reference artwork while
    designing a font. Zoom, scroll, fit and print the image without editing it.
Setup:
    FontLab9, Python3.11, Fly and App>=0.2.156.dev0. No open font is
    required. Use FontLab's existing Qt runtime; install no alternate Qt binding.
Run:
    Open chooses a readable image. Cancel keeps the current view. Invalid files
    leave its image and zoom unchanged. Use View for zoom, Normal and Fit. Print
    opens an asynchronous owned printer dialog only on your explicit action.
Result:
    Free zoom preserves the current scale when Fit is switched off. Printing draws the original image at the printer origin.
Compatibility:
    Close/Escape releases owned dialogs, painters and callbacks. Inputs and font
    data are unchanged. Native PythonQt/printer and whole-font acceptance remain
    pending. Original source: rescued/part2/ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py

Run **Tools > Font Reference Image Viewer** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1886765eaabc607d4d6edbf2bd6d5cba8df6c8e6b1aa0dc9a1b0231367a5b06e.py)
<!--/codeinclude-->
