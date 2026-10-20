# Examples: xmlpatterns

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, now preserved under `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

1 records: 1 implemented, 0 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [Official schema](#official-schema) | implemented | passed | Apache-2.0 |

### Official schema

- Source: [pyqt/examples / src/pyqt-official/xmlpatterns/schema/schema.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/xmlpatterns/schema/schema.py)
- Port: [`ports/xmlpatterns/pyqt-official/schema-1e5d0f7289e1b36e.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/xmlpatterns/pyqt-official/schema-1e5d0f7289e1b36e.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run08.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("1e5d0f7289e1b36e")  # inside FontLab
examples.close("1e5d0f7289e1b36e")
```
