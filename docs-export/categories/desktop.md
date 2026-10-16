# Examples: desktop

2 records: 2 implemented, 0 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [Official screenshot](#official-screenshot) | implemented | passed | Apache-2.0 |
| [Official systray](#official-systray) | implemented | passed | Apache-2.0 |

### Official screenshot

- Source: [pyqt/examples / src/pyqt-official/desktop/screenshot.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/desktop/screenshot.py)
- Port: [`ports/desktop/pyqt-official/screenshot-65d15d1fbc1b15e9.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/desktop/pyqt-official/screenshot-65d15d1fbc1b15e9.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("65d15d1fbc1b15e9")  # inside FontLab
examples.close("65d15d1fbc1b15e9")
```

### Official systray

- Source: [pyqt/examples / src/pyqt-official/desktop/systray/systray.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/desktop/systray/systray.py)
- Port: [`ports/desktop/pyqt-official/systray-c1b878b63f80e733.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/desktop/pyqt-official/systray-c1b878b63f80e733.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("c1b878b63f80e733")  # inside FontLab
examples.close("c1b878b63f80e733")
```
