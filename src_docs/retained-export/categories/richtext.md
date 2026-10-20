# Examples: richtext

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, now preserved under `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

3 records: 3 implemented, 0 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [Official calendar](#official-calendar) | implemented | passed | Apache-2.0 |
| [Official orderform](#official-orderform) | implemented | passed | Apache-2.0 |
| [Official syntaxhighlighter](#official-syntaxhighlighter) | implemented | passed | Apache-2.0 |

### Official calendar

- Source: [pyqt/examples / src/pyqt-official/richtext/calendar.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/richtext/calendar.py)
- Port: [`ports/richtext/pyqt-official/calendar-c56cf1699b07b350.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/richtext/pyqt-official/calendar-c56cf1699b07b350.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("c56cf1699b07b350")  # inside FontLab
examples.close("c56cf1699b07b350")
```

### Official orderform

- Source: [pyqt/examples / src/pyqt-official/richtext/orderform.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/richtext/orderform.py)
- Port: [`ports/richtext/pyqt-official/orderform-c997677a2bdb4f34.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/richtext/pyqt-official/orderform-c997677a2bdb4f34.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("c997677a2bdb4f34")  # inside FontLab
examples.close("c997677a2bdb4f34")
```

### Official syntaxhighlighter

- Source: [pyqt/examples / src/pyqt-official/richtext/syntaxhighlighter.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/richtext/syntaxhighlighter.py)
- Port: [`ports/richtext/pyqt-official/syntaxhighlighter-428c50abcef7adfe.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/richtext/pyqt-official/syntaxhighlighter-428c50abcef7adfe.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("428c50abcef7adfe")  # inside FontLab
examples.close("428c50abcef7adfe")
```
