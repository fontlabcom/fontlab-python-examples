---
this_file: PLAN.md
---

# Complete PythonQt example ports

Port the complete https://github.com/pyqt/examples and
https://github.com/eyllanesc/QtExamples collections into this repository for
FontLab's PythonQt runtime. The repeated pyqt URL is one source collection;
both distinct repositories are required, including numbered examples, official
demos/examples and additional QtExamples entries.

1. Pin each upstream revision; inventory every executable example and resource,
   preserve recoverable original bytes/hashes, and record per-file provenance.
2. Resolve licenses and attribution per example/resource. Upstream distinguishes
   MIT/GPL numbered examples, GPL official demos and separately licensed images;
   QtExamples is GPL-3.0. This repository's existing license does not relicense
   those inputs; inspect individual file/resource terms in both repositories.
3. Map every upstream entry to an organized port/category and index. Keep the
   full denominator, with implementation and native verification states.
4. Port Qt6/PyQt calls to actual available PythonQt/Qt5 semantics. Reuse FontLab's
   QApplication/event loop and shared compatibility layers; do not load PyQt,
   PySide or another Qt runtime into the host. Include UI/resources, models,
   graphics/painting, QML, database, network, platform, multimedia/GStreamer,
   video overlays and matplotlib integration examples in scope.
5. Supply simple in-host and external launch instructions, scoped lifetimes and
   clean teardown. Execute each example with owned data/UI, recording interaction,
   output artifacts, errors and cleanup. Do not alter user fonts or settings.
6. Review every port, verify all inventory mappings and original-source recovery,
   and rebuild ecosystem documentation with categorized examples and exact status.

Source acquisition and the complete static catalog are now verified: both pinned
trees retain all 1,569 original file mappings and 465 Python files. The categorized
index and receipt-driven tool are available under `catalog/` and `tools/`.
Observed source requirements and per-file license evidence are recorded. The
separate `catalog/ports.json` now records four implemented numbered ports and the
required exact Designer resource, with individual MIT review and attribution.
Their native source-load acceptance passed; other implementation, native and
license reviews remain required. The static catalog is retained unchanged.
The 298 Python entrypoint candidates, 14 ambiguous Python candidates and 3 QML
launcher candidates require review before establishing an executable denominator.
The remaining 153 Python files are auxiliary; 69 shared/repository files retain
explicit unresolved ownership and their individual planned mappings.
Execution evidence now excludes deferred function/async/method/lambda bodies
and retains executing class bodies/headers and definition-time expressions.
Conditions and function calls require source review; broad import/API/capability
evidence stays complete. The pinned catalog reproduces unchanged after this fix.

Completion requires all source examples accounted for and ported with actual
FontLab acceptance. Static compilation and a selected sample do not prove the
complete collection. A missing host API remains a tracked implementation gap.

The first implementation batch covers QLabel (`ce3e17a7a2a03a02`), QVBoxLayout
(`f5ddfd0eaacbf845`), Signals and Slots (`79cc15680bc2cebb`) and Qt Designer
(`402068f40005cd66`). `fontlab_python_examples` supplies named launch/inspect/close,
module-retained native handles and `fontlabapp.widgets.OwnedWidget` cleanup;
`examples/remopy.py` demonstrates ordinary external execution in FontLab.
Actual FontLab source-load checks now verify original text/layout, real alert
click/dismiss/repeat, Designer OK/Cancel, retained state across isolated requests
and destruction of38 tracked owned objects with the host still running.
verification/first-native-batch.json retains that bounded batch evidence;
complete-collection completion is not inferred from it or boundary tests.
