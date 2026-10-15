---
this_file: clean-room-specs/36246fcbffecdeba.md
---

# Declarative canvas collection

## Purpose

Demonstrate declarative canvas collection through an independently written FontLab example.

## Capability boundary

Current FontLab behaviour is a capability exception during launch, before constructing UI, registering a service, starting a timer or performing external work. Use a freshly worded short diagnostic naming the absent Qt facility. Do not simulate success or substitute another Qt runtime. The supported-host description below is behavioural context, not a request to implement missing host modules.

## Visible UI

Supported-host intent: a launcher list of seven 2D drawing scenes.

## Interactions and results

Open examples covering a heart, speech bubble, rounded square, rounded rectangle, face, clipping and an animal illustration.

## Data and algorithms

Use canvas paths with cubic/quadratic curves, arcs, clipping and fills; loading requires the missing QQuickView/declarative modules.

## Resources

Draw new path artwork, especially an original animal picture; no reference paths or images.

Create any required data, artwork, translations and form descriptions independently. Exact sample prose, names, pixels and ornamental geometry are not acceptance requirements.

## FontLab and PythonQt constraints

Use the Python interpreter and event loop already running inside FontLab. Widgets come from PythonQt.QtGui; PythonQt.QtWidgets is unavailable. Do not import another Qt binding or construct QApplication. Open dialogs asynchronously. Keep all created windows, timers, signal connections and workers under one owned lifetime; stop work and disconnect callbacks before native deletion. Closing an example must leave FontLab running.

PythonQt wrapper arithmetic is hazardous: unary negation can crash the process. Work with numeric coordinate components instead. A slot cannot rely on sender(), which yields None; bind its source explicitly. Native wrappers reject extra Python attributes and subclasses cannot shadow native method names. Use explicit native base dispatch for protected event handlers. Construct value wrappers explicitly when enum conversion fails; item views may return a different wrapper from the Python subclass. Keep Python state separately where necessary. QObject is exposed through PythonQt.private; native list and table models belong to PythonQt.QtGui. Stored QSettings sequences can return tuples, so make a mutable list before changes. Screen discovery should use QApplication.screens(), since primaryScreen is unreliable in this binding. Check constructor overloads individually: some accept keywords and others require positional arguments. Never mutate open fonts or global application preferences.

## Acceptance checks

Current host: reject before loading. Future supported host: browse all scenes, verify curve/clip output and return navigation.

Run interaction checks in an owned no-document test session. Launch and close twice; confirm the host remains responsive and no owned windows, callbacks, timers, workers, sockets or temporary outputs survive. For blocked examples, successful verification means the explicit capability failure and zero side effects; supported-host checks are conditional on those APIs becoming available. These are test instructions, not claims of a new native run.
