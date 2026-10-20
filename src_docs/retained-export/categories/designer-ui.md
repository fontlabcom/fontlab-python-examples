# Examples: designer-ui

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, now preserved under `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

8 records: 6 implemented, 2 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [Official calculatorform](#official-calculatorform) | implemented | passed | Apache-2.0 |
| [Official compile-on-the-fly](#official-compile-on-the-fly) | implemented | passed | Apache-2.0 |
| [Official formextractor](#official-formextractor) | blocked | not run | Apache-2.0 |
| [Official load_ui1](#official-load_ui1) | implemented | passed | Apache-2.0 |
| [Official load_ui2](#official-load_ui2) | implemented | passed | Apache-2.0 |
| [Official sharedmemory](#official-sharedmemory) | blocked | not run | Apache-2.0 |
| [Official simpledommodel](#official-simpledommodel) | implemented | passed | Apache-2.0 |
| [Qt Designer](#qt-designer) | implemented | passed | MIT |

### Official calculatorform

- Source: [pyqt/examples / src/pyqt-official/designer/calculatorform/calculatorform.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/designer/calculatorform/calculatorform.py)
- Port: [`ports/designer/pyqt-official/calculatorform-27bf65f8b059fd96.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/designer/pyqt-official/calculatorform-27bf65f8b059fd96.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("27bf65f8b059fd96")  # inside FontLab
examples.close("27bf65f8b059fd96")
```

### Official compile-on-the-fly

- Source: [pyqt/examples / src/pyqt-official/pyuic/compile-on-the-fly.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/pyuic/compile-on-the-fly.py)
- Port: [`ports/pyuic/pyqt-official/compile-on-the-fly-5a8e48d2a1396cea.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/pyuic/pyqt-official/compile-on-the-fly-5a8e48d2a1396cea.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run07.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("5a8e48d2a1396cea")  # inside FontLab
examples.close("5a8e48d2a1396cea")
```

### Official formextractor

- Source: [pyqt/examples / src/pyqt-official/webkit/formextractor/formextractor.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/webkit/formextractor/formextractor.py)
- Port: [`ports/webkit/pyqt-official/formextractor-6ed36280660df7ea.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/webkit/pyqt-official/formextractor-6ed36280660df7ea.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab.

### Official load_ui1

- Source: [pyqt/examples / src/pyqt-official/pyuic/load_ui1.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/pyuic/load_ui1.py)
- Port: [`ports/pyuic/pyqt-official/load-ui1-b7db02f540cc7559.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/pyuic/pyqt-official/load-ui1-b7db02f540cc7559.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run07.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("b7db02f540cc7559")  # inside FontLab
examples.close("b7db02f540cc7559")
```

### Official load_ui2

- Source: [pyqt/examples / src/pyqt-official/pyuic/load_ui2.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/pyuic/load_ui2.py)
- Port: [`ports/pyuic/pyqt-official/load-ui2-b9660f4ee653ca01.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/pyuic/pyqt-official/load-ui2-b9660f4ee653ca01.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run07.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("b9660f4ee653ca01")  # inside FontLab
examples.close("b9660f4ee653ca01")
```

### Official sharedmemory

- Source: [pyqt/examples / src/pyqt-official/ipc/sharedmemory/sharedmemory.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/ipc/sharedmemory/sharedmemory.py)
- Port: [`ports/ipc/pyqt-official/sharedmemory-de35a965dfcfd678.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/ipc/pyqt-official/sharedmemory-de35a965dfcfd678.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QSharedMemory lacks detach and a documented usable byte buffer in FontLab.

### Official simpledommodel

- Source: [pyqt/examples / src/pyqt-official/itemviews/simpledommodel.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/itemviews/simpledommodel.py)
- Port: [`ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("a59dae9770bfbefb")  # inside FontLab
examples.close("a59dae9770bfbefb")
```

### Qt Designer

- Source: [pyqt/examples / src/05 Qt Designer Python/main.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/05%20Qt%20Designer%20Python/main.py)
- Port: [`ports/designer-ui/pyqt-examples/main-402068f40005cd66.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/designer-ui/pyqt-examples/main-402068f40005cd66.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `701df4d`; workspace evidence `verification/first-native-batch.json`)
- Licence: MIT

```python
import fontlab_python_examples as examples

handle = examples.launch("402068f40005cd66")  # inside FontLab
examples.close("402068f40005cd66")
```
