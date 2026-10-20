---
this_file: src_docs/md/insights/worker-glyph-queue.md
tags:
- PythonQt
categories:
- Examples
---

# Worker glyph audit queue

Worker-to-GUI queue hand-off.

The retained catalogue records these interaction checks: Click start twice: one worker; wait for four GUI-delivered results; restart then stop or close immediately; worker joined, no Qt calls from worker.

This is an archived example. Review its imports and host assumptions before running it.

## Source

```python
--8<-- "src_docs/retained-insights/worker-glyph-queue.py.txt"
```
