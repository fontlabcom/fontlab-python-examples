---
this_file: clean-room-specs/c82d1af7d1a7b0cf.md
---

# Native versus GL painter comparison

## Purpose

Demonstrate native versus GL painter comparison through an independently written FontLab example.

## Visible UI

Side-by-side native QWidget and QOpenGLWidget canvases, labeled by renderer.

## Interactions and results

Both animate the same circle composition together with a short text specimen; there are no editing controls.

## Data and algorithms

At fifty-millisecond intervals update a shared phase. Paint thirty colored circles and text through QPainter in both canvases. Apply multisampling only to the owned GL widget.

## Resources

No external resources; use a fresh short text specimen and procedural geometry.

Create any required data, artwork, translations and form descriptions independently. Exact sample prose, names, pixels and ornamental geometry are not acceptance requirements.

## FontLab and PythonQt constraints

Use the Python interpreter and event loop already running inside FontLab. Widgets come from PythonQt.QtGui; PythonQt.QtWidgets is unavailable. Do not import another Qt binding or construct QApplication. Open dialogs asynchronously. Keep all created windows, timers, signal connections and workers under one owned lifetime; stop work and disconnect callbacks before native deletion. Closing an example must leave FontLab running.

PythonQt wrapper arithmetic is hazardous: unary negation can crash the process. Work with numeric coordinate components instead. A slot cannot rely on sender(), which yields None; bind its source explicitly. Native wrappers reject extra Python attributes and subclasses cannot shadow native method names. Use explicit native base dispatch for protected event handlers. Construct value wrappers explicitly when enum conversion fails; item views may return a different wrapper from the Python subclass. Keep Python state separately where necessary. QObject is exposed through PythonQt.private; native list and table models belong to PythonQt.QtGui. Stored QSettings sequences can return tuples, so make a mutable list before changes. Screen discovery should use QApplication.screens(), since primaryScreen is unreliable in this binding. Check constructor overloads individually: some accept keywords and others require positional arguments. Never mutate open fonts or global application preferences.

## Acceptance checks

Compare both views across frames and resizing; verify synchronized content and no global surface-format mutation. Close during animation and confirm timer cleanup.

Run interaction checks in an owned no-document test session. Launch and close twice; confirm the host remains responsive and no owned windows, callbacks, timers, workers, sockets or temporary outputs survive. For blocked examples, successful verification means the explicit capability failure and zero side effects; supported-host checks are conditional on those APIs becoming available. These are test instructions, not claims of a new native run.
