---
this_file: src_docs/md/insights/compiled-slot-exposure.md
tags:
- PythonQt
categories:
- Examples
---

# Compiled wrapper and slot exposure

C++ decorators, slots and metaobject exposure.

The retained catalogue records these interaction checks: Click move: compiled non-slot move(QPoint) repositions preview; clear invokes native clear() slot; inspect its metaobject slot index; no custom C++ compilation.

This is an archived example. Review its imports and host assumptions before running it.

## Source

```python
--8<-- "src_docs/retained-insights/compiled-slot-exposure.py.txt"
```
