# Insight examples

Original examples written for FontLab's PythonQt, each showing one idiom.

| Example | Idiom | Native | Licence |
| --- | --- | --- | --- |
| [Tracked signal lifetime](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/signal-lifetime.py) | String-signature connects and owned wrapper lifetime | passed | Apache-2.0 |
| [Glyph name list](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/glyph-list.py) | Model/view separation with QStringListModel | passed | Apache-2.0 |
| [Sample glyph metrics](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/metrics-table.py) | Read-only QAbstractTableModel callbacks | passed | Apache-2.0 |
| [Incremental glyph audit](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/timer-batch.py) | QTimer-driven bounded GUI work | passed | Apache-2.0 |
| [Contour canvas](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/contour-canvas.py) | Custom painting with genuine QPainterPath | passed | Apache-2.0 |
| [Owned key observer](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/owned-key-filter.py) | QObject event filter scoped to owned widget | passed | Apache-2.0 |
| [Synchronized advance controls](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/metric-controls.py) | Signal blocking to avoid control feedback | passed | Apache-2.0 |
| [Glyph role properties](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/glyph-properties.py) | Qt attributes and dynamic QObject properties | passed | Apache-2.0 |
| [Owned proof settings](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/sandbox-settings.py) | QSettings persistence in an isolated namespace | passed | Apache-2.0 |
| [Advance input errors](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/callback-errors.py) | Narrow callback error handling in owned UI | passed | Apache-2.0 |
| [Owned metrics dock](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/owned-dock.py) | Dock/panel composition without host UI mutation | passed | Apache-2.0 |
| [Contour graphics scene](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/contour-scene.py) | QGraphicsScene ownership and view navigation | passed | Apache-2.0 |
| [Loaded glyph metrics form](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/loaded-glyph-form.py) | QUiLoader and object-name lookup | passed | Apache-2.0 |
| [Worker glyph audit queue](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/worker-glyph-queue.py) | Worker-to-GUI queue hand-off | passed | Apache-2.0 |
| [Owned sample-data console](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/owned-repl.py) | Owned console/REPL widgets | passed | Apache-2.0 |
| [Owned menu plug-in tokens](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/plugin-tokens.py) | Registration and explicit unload | passed | Apache-2.0 |
| [Undo sample glyph metrics](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/metrics-undo.py) | Undo integration on owned data | passed | Apache-2.0 |
| [Compiled wrapper and slot exposure](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/insights/compiled-slot-exposure.py) | C++ decorators, slots and metaobject exposure | passed | Apache-2.0 |

```python
import fontlab_python_examples as examples

examples.launch("signal-lifetime")  # by slug, inside FontLab
```
