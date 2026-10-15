---
this_file: clean-room-specs/e63bffc17abf2fde.md
---

# Falling-block game

## Purpose

Demonstrate falling-block game through an independently written FontLab example.

## Visible UI

A ten-column, twenty-two-row board with next-piece preview, score/level/line displays and Start/Pause/Quit.

## Interactions and results

Start resets play. Left/right move, down/up rotate oppositely, Space hard-drops, D lowers one row. Pause freezes and resumes; blocked spawning ends play.

## Data and algorithms

Choose among seven tetromino shapes. Remove full rows and collapse above them; score each placement by drop distance plus seven and each removed row by ten. Increase level every twenty-five pieces; timer interval is one second divided by one plus level.

## Resources

Paint new colored block faces procedurally; no assets.

Create any required data, artwork, translations and form descriptions independently. Exact sample prose, names, pixels and ornamental geometry are not acceptance requirements.

## FontLab and PythonQt constraints

Use the Python interpreter and event loop already running inside FontLab. Widgets come from PythonQt.QtGui; PythonQt.QtWidgets is unavailable. Do not import another Qt binding or construct QApplication. Open dialogs asynchronously. Keep all created windows, timers, signal connections and workers under one owned lifetime; stop work and disconnect callbacks before native deletion. Closing an example must leave FontLab running.

PythonQt wrapper arithmetic is hazardous: unary negation can crash the process. Work with numeric coordinate components instead. A slot cannot rely on sender(), which yields None; bind its source explicitly. Native wrappers reject extra Python attributes and subclasses cannot shadow native method names. Use explicit native base dispatch for protected event handlers. Construct value wrappers explicitly when enum conversion fails; item views may return a different wrapper from the Python subclass. Keep Python state separately where necessary. QObject is exposed through PythonQt.private; native list and table models belong to PythonQt.QtGui. Stored QSettings sequences can return tuples, so make a mutable list before changes. Screen discovery should use QApplication.screens(), since primaryScreen is unreliable in this binding. Check constructor overloads individually: some accept keywords and others require positional arguments. Never mutate open fonts or global application preferences.

## Acceptance checks

Move/rotate against walls, hard-drop, clear rows, pause/resume and fill to game over. Verify scoring, next preview and reset; Quit affects only this example.

Run interaction checks in an owned no-document test session. Launch and close twice; confirm the host remains responsive and no owned windows, callbacks, timers, workers, sockets or temporary outputs survive. For blocked examples, successful verification means the explicit capability failure and zero side effects; supported-host checks are conditional on those APIs becoming available. These are test instructions, not claims of a new native run.
