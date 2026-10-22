# Examples: draganddrop

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

2 records: 2 implemented, 0 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [Official draggabletext](#official-draggabletext) | implemented | passed | Apache-2.0 |
| [Official dropsite](#official-dropsite) | implemented | passed | Apache-2.0 |

### Official draggabletext

- Source: [pyqt/examples / src/pyqt-official/draganddrop/draggabletext/draggabletext.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/draganddrop/draggabletext/draggabletext.py)
- Port: [`ports/draganddrop/pyqt-official/draggabletext-700e96dec485e7a8.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/draganddrop/pyqt-official/draggabletext-700e96dec485e7a8.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run01.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("700e96dec485e7a8")  # inside FontLab
examples.close("700e96dec485e7a8")
```

### Official dropsite

- Source: [pyqt/examples / src/pyqt-official/draganddrop/dropsite.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/draganddrop/dropsite.py)
- Port: [`ports/draganddrop/pyqt-official/dropsite-fa6823667fdb918f.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/draganddrop/pyqt-official/dropsite-fa6823667fdb918f.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("fa6823667fdb918f")  # inside FontLab
examples.close("fa6823667fdb918f")
```
