---
this_file: docs/insights-second-batch.md
---

# Insight ranks 13–18: controller checks

All six examples are original Apache-2.0 code; native acceptance is unexecuted.
Launch each slug with `examples.launch(slug)`, drive the native controls through
`examples.get(slug).controls`, and query `examples.inspect(slug)` after each action.
The controls dictionary belongs to ExampleHandle, never a native instance.
Named close disconnects exact receivers, releases state and closes only owned UI.
Repeat close, relaunch, then close again; verify FontLab remains responsive and
fonts/preferences/Output unchanged. Record native acceptance in insights.json.

| Rank / slug | Controls dictionary keys | Native check |
| --- | --- | --- |
| 13. `loaded-glyph-form` | `glyph_name`, `advance`, `apply`, `result`, `form` | Set glyph_name.text and advance.value, click apply; result and inspection agree; load from another working directory; close/relaunch. |
| 14. `worker-glyph-queue` | `start`, `stop`, `timer`, `log` | Click start twice: one worker; wait for four GUI-delivered results; restart then stop or close immediately; worker joined, no Qt calls from worker. |
| 15. `owned-repl` | `input`, `run`, `reset`, `output` | Run advance, assignment advance = 720, print(advance), and invalid syntax; all output stays in the owned console; reset restores the namespace. |
| 16. `plugin-tokens` | `install`, `unload`, `plugin_action`, `status` | Install twice: one menu/action token pair; trigger plugin_action; unload twice: zero tokens and detached menu; reinstall works; FontLab menus unchanged. |
| 17. `metrics-undo` | `advance`, `apply`, `undo`, `redo`, `stack`, `status` | Apply two advances, undo/redo; undo then apply a new value clears redo branch; native command overrides and label update work; close safely. |
| 18. `compiled-slot-exposure` | `move`, `clear`, `input`, `preview`, `status` | Click move: compiled non-slot move(QPoint) repositions preview; clear invokes native clear() slot; inspect its metaobject slot index; no custom C++ compilation. |

## Behavior and ownership

The loaded form is an original adjacent .ui file, opened via QFile/QUiLoader.
Its XML has no implicit connections: the Apply receiver is tracked at runtime.
File/loader temporaries are closed/deleted on success or failure; the form is
parented to the owned root. Missing named controls fail and roll back the build.

The worker starts only after Start; it handles four sample names as Python data.
Repeated Start while running is ignored. An eight-entry queue is drained in
bounded GUI timer ticks. Stop sets a cancellation event and joins before cleanup;
completion and calculation errors also stop/join. No Qt wrapper enters the worker.

The console runs short expressions/statements in its own globals, initialized
with advance and glyph_names. Its small builtins mapping sends print output to
its owned text widget; evaluation/errors never redirect stdout or global hooks.
Reset restores the sample globals. This is an example console, not a security
sandbox; use short sample commands. No FontLab imports are supplied.

The plug-in begins unloaded: plugin_action is None. Install allocates one owned
menu and action, retained under the stable proof-menu/advance-action tokens.
A second Install changes nothing. After Install, plugin_action.trigger() invokes
the sample handler. Unload disconnects the exact stored signal, removes menu
entries, drops tokens and schedules menu deletion; the menu owns its action.
A failed disconnect preserves the registration and prevents deletion. No actions
are attached to FontLab menus, and closing the example unloads any registration.

The undo example requires real QtGui.QUndoStack and QUndoCommand. It pushes
Python command subclasses that alter only a sample advance; a tracked indexChanged
receiver updates the label. Controls expose stack for native inspection. Qt
properties index/canUndo/canRedo are attributes; count() is a method. The stack
owns commands, including redo branches discarded on a new push. Retained Python
command receivers are released after stack.clear(), following disconnection.
Native virtual callbacks, ownership transfer and command deletion require actual
controller acceptance; no command is manually deleted.

The compiled exposure example uses wrappers already built into PythonQt:
constructors, the wrapped QWidget.move(QPoint) method and the native clear() slot.
It checks QLineEdit's metaobject slot index, connects Clear to the retained native
bound method, and reports the real preview position. It compiles/registers no
C++ extension and calls no help() that might print to Output. Missing exported
classes or slots raise a clear host capability error instead of a substitute.

## Documentation consulted

[PythonQt developer: decorators and ownership](https://mevislab.github.io/pythonqt/Developer.html),
[QUiLoader](https://doc.qt.io/qt-5/quiloader.html),
[QUndoStack](https://doc.qt.io/qt-5/qundostack.html),
[QUndoCommand](https://doc.qt.io/qt-5/qundocommand.html), and
[QMetaObject](https://doc.qt.io/qt-5/qmetaobject.html).
C++ contracts inform arguments and ownership; measured FontLab module placement
and attribute restrictions govern the implementations. No new dependency.
