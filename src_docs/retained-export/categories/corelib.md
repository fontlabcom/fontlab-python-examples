# Examples: corelib

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, now preserved under `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

4 records: 2 implemented, 2 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [QtExamples corelib/ipc/localfortuneclient/main](#qtexamples-corelibipclocalfortuneclientmain) | implemented | passed | GPL-3.0-only |
| [QtExamples corelib/ipc/localfortuneserver/main](#qtexamples-corelibipclocalfortuneservermain) | implemented | passed | GPL-3.0-only |
| [QtExamples corelib/ipc/sharedmemory/dialog_ui](#qtexamples-corelibipcsharedmemorydialog_ui) | blocked | not run | GPL-3.0-only |
| [QtExamples corelib/ipc/sharedmemory/main](#qtexamples-corelibipcsharedmemorymain) | blocked | not run | GPL-3.0-only |

### QtExamples corelib/ipc/localfortuneclient/main

- Source: [eyllanesc/QtExamples / official/corelib/ipc/localfortuneclient/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/corelib/ipc/localfortuneclient/main.py)
- Port: [`ports/corelib/eyllanesc/main-4bc27e706ac146f5.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/corelib/eyllanesc/main-4bc27e706ac146f5.py)
- Implementation: **implemented**
- Native acceptance: passed (historical record; workspace evidence `examples-interactions/native-lic-final2.jsonl`)
- Licence: GPL-3.0-only

```python
import fontlab_python_examples as examples

handle = examples.launch("4bc27e706ac146f5")  # inside FontLab
examples.close("4bc27e706ac146f5")
```

### QtExamples corelib/ipc/localfortuneserver/main

- Source: [eyllanesc/QtExamples / official/corelib/ipc/localfortuneserver/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/corelib/ipc/localfortuneserver/main.py)
- Port: [`ports/corelib/eyllanesc/main-cb1871959e42607b.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/corelib/eyllanesc/main-cb1871959e42607b.py)
- Implementation: **implemented**
- Native acceptance: passed (historical record; workspace evidence `examples-interactions/native-lic-final2.jsonl`)
- Licence: GPL-3.0-only

```python
import fontlab_python_examples as examples

handle = examples.launch("cb1871959e42607b")  # inside FontLab
examples.close("cb1871959e42607b")
```

### QtExamples corelib/ipc/sharedmemory/dialog_ui

- Source: [eyllanesc/QtExamples / official/corelib/ipc/sharedmemory/dialog_ui.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/corelib/ipc/sharedmemory/dialog_ui.py)
- Port: [`ports/corelib/eyllanesc/dialog-ui-04e8e49f95de6cf5.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/corelib/eyllanesc/dialog-ui-04e8e49f95de6cf5.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt.QtCore.QSharedMemory lacks detach(). The associated Dialog requires native shared-memory image exchange and explicit detach; the generated UI entrypoint launches that same Dialog. An owned segment cannot be implemented and safely released.

### QtExamples corelib/ipc/sharedmemory/main

- Source: [eyllanesc/QtExamples / official/corelib/ipc/sharedmemory/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/corelib/ipc/sharedmemory/main.py)
- Port: [`ports/corelib/eyllanesc/main-24b0b2aa8998d701.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/corelib/eyllanesc/main-24b0b2aa8998d701.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt.QtCore.QSharedMemory lacks detach(). The associated Dialog requires native shared-memory image exchange and explicit detach; the generated UI entrypoint launches that same Dialog. An owned segment cannot be implemented and safely released.
