# this_file: Scripts/Tools/Font Reference Image Viewer.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect font reference artwork with the complete original image viewer.

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
    pending. Historical source: rescued/part2/ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py
"""
# historical source sha256: 03e04bedb750535fbf3bf59fc9b3d90eda75890a8731f804204da0b9af1325ca


def main() -> None:
    """Open this source-distinct reference viewer through Fly's lazy App alias."""
    from fly.ap.image_viewer import show

    show()


if __name__ == "__main__":
    main()
