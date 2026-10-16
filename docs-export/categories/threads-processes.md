# Examples: threads-processes

4 records: 2 implemented, 2 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [Official plugins](#official-plugins) | blocked | not run | Apache-2.0 |
| [Official semaphores](#official-semaphores) | implemented | passed | Apache-2.0 |
| [Official waitconditions](#official-waitconditions) | implemented | passed | Apache-2.0 |
| [QtExamples main](#qtexamples-main) | blocked | not run | GPL-3.0-only |

### Official plugins

- Source: [pyqt/examples / src/pyqt-official/designer/plugins/plugins.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/designer/plugins/plugins.py)
- Port: [`ports/designer/pyqt-official/plugins-960c701fa6221ac5.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/designer/pyqt-official/plugins-960c701fa6221ac5.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtDesigner plugin interfaces and the Python Designer plugin loader are unavailable

### Official semaphores

- Source: [pyqt/examples / src/pyqt-official/threads/semaphores.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/threads/semaphores.py)
- Port: [`ports/threads/pyqt-official/semaphores-b95b687bbc541207.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/threads/pyqt-official/semaphores-b95b687bbc541207.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("b95b687bbc541207")  # inside FontLab
examples.close("b95b687bbc541207")
```

### Official waitconditions

- Source: [pyqt/examples / src/pyqt-official/threads/waitconditions.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/threads/waitconditions.py)
- Port: [`ports/threads/pyqt-official/waitconditions-27709a02d37b9ba9.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/threads/pyqt-official/waitconditions-27709a02d37b9ba9.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("27709a02d37b9ba9")  # inside FontLab
examples.close("27709a02d37b9ba9")
```

### QtExamples main

- Source: [eyllanesc/QtExamples / official/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/main.py)
- Port: [`ports/threads-processes/eyllanesc/main-a207ef153f0b81b7.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/threads-processes/eyllanesc/main-a207ef153f0b81b7.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original launcher spawns sys.executable with a PyQt5/PySide2 binding and launches quickcontrols2/gallery, which requires absent QtQml/QtQuick/QtQuickControls2. PythonQt also has no Python Signal/Slot declaration API. Replacing it with the in-host examples launcher changes its subprocess/binding-selection behavior; it is blocked.
