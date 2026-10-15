---
this_file: clean-room-specs/ed6d42d4faa7e0bb.md
---

# Shared textured GL views

## Purpose

Demonstrate shared textured GL views through an independently written FontLab example.

## Capability boundary

Current FontLab behaviour is a capability exception during launch, before constructing UI, registering a service, starting a timer or performing external work. Use a freshly worded short diagnostic naming the absent Qt facility. Do not simulate success or substitute another Qt runtime. The supported-host description below is behavioural context, not a request to implement missing host modules.

## Visible UI

Supported-host intent: a grid of GL views containing textured rotating objects with different background colors.

## Interactions and results

Select a view, drag it and let its object continue rotating; selection determines which view timer motion affects.

## Data and algorithms

Share texture resources across owned contexts; map newly drawn images onto independently constructed faces. The required version-specific GL API is absent.

## Resources

Draw new contrasting texture panels; never reuse reference artwork.

Create any required data, artwork, translations and form descriptions independently. Exact sample prose, names, pixels and ornamental geometry are not acceptance requirements.

## FontLab and PythonQt constraints

Use the Python interpreter and event loop already running inside FontLab. Widgets come from PythonQt.QtGui; PythonQt.QtWidgets is unavailable. Do not import another Qt binding or construct QApplication. Open dialogs asynchronously. Keep all created windows, timers, signal connections and workers under one owned lifetime; stop work and disconnect callbacks before native deletion. Closing an example must leave FontLab running.

PythonQt wrapper arithmetic is hazardous: unary negation can crash the process. Work with numeric coordinate components instead. A slot cannot rely on sender(), which yields None; bind its source explicitly. Native wrappers reject extra Python attributes and subclasses cannot shadow native method names. Use explicit native base dispatch for protected event handlers. Construct value wrappers explicitly when enum conversion fails; item views may return a different wrapper from the Python subclass. Keep Python state separately where necessary. QObject is exposed through PythonQt.private; native list and table models belong to PythonQt.QtGui. Stored QSettings sequences can return tuples, so make a mutable list before changes. Screen discovery should use QApplication.screens(), since primaryScreen is unreliable in this binding. Check constructor overloads individually: some accept keywords and others require positional arguments. Never mutate open fonts or global application preferences.

## Acceptance checks

Current host: fail before context/texture creation. Future supported host: switch active views, rotate, resize and verify shared texture lifetime.

Run interaction checks in an owned no-document test session. Launch and close twice; confirm the host remains responsive and no owned windows, callbacks, timers, workers, sockets or temporary outputs survive. For blocked examples, successful verification means the explicit capability failure and zero side effects; supported-host checks are conditional on those APIs becoming available. These are test instructions, not claims of a new native run.
