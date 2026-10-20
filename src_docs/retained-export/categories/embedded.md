# Examples: embedded

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, now preserved under `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

2 records: 2 implemented, 0 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [QtExamples embedded/lightmaps/main](#qtexamples-embeddedlightmapsmain) | implemented | passed | GPL-3.0-only |
| [QtExamples embedded/styleexample/main](#qtexamples-embeddedstyleexamplemain) | implemented | passed | GPL-3.0-only |

### QtExamples embedded/lightmaps/main

- Source: [eyllanesc/QtExamples / official/embedded/lightmaps/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/embedded/lightmaps/main.py)
- Port: [`ports/embedded/eyllanesc/main-92fc3cf4b5dd009c.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/embedded/eyllanesc/main-92fc3cf4b5dd009c.py)
- Implementation: **implemented**
- Native acceptance: passed (historical record; workspace evidence `examples-interactions/native-lic-final2.jsonl`)
- Licence: GPL-3.0-only

```python
import fontlab_python_examples as examples

handle = examples.launch("92fc3cf4b5dd009c")  # inside FontLab
examples.close("92fc3cf4b5dd009c")
```

### QtExamples embedded/styleexample/main

- Source: [eyllanesc/QtExamples / official/embedded/styleexample/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/embedded/styleexample/main.py)
- Port: [`ports/embedded/eyllanesc/main-631cc1bc310c00b9.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/embedded/eyllanesc/main-631cc1bc310c00b9.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `b9ead3f`; workspace evidence `examples-resources/acceptance02.jsonl`)
- Licence: GPL-3.0-only

```python
import fontlab_python_examples as examples

handle = examples.launch("631cc1bc310c00b9")  # inside FontLab
examples.close("631cc1bc310c00b9")
```
