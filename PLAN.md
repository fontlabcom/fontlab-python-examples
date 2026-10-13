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

Completion requires all source examples accounted for and ported with actual
FontLab acceptance. Static compilation and a selected sample do not prove the
complete collection. A missing host API remains a tracked implementation gap.
