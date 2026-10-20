---
this_file: src_docs/md/insights/signal-lifetime.md
tags:
- PythonQt
categories:
- Examples
---

# Tracked signal lifetime

String-signature connects and owned wrapper lifetime.

The retained catalogue records these interaction checks: Click twice: advance 600 → 610 → 620; reshow retains identity; close/relaunch resets safely.

This is an archived example. Review its imports and host assumptions before running it.

## Source

```python
--8<-- "src_docs/retained-insights/signal-lifetime.py.txt"
```
