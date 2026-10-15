# Examples: graphics-painting

56 records: 42 implemented, 14 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [Official 2dpainting](#official-2dpainting) | implemented | passed | Apache-2.0 |
| [Official analogclock](#official-analogclock) | implemented | passed | Apache-2.0 |
| [Official anchorlayout](#official-anchorlayout) | implemented | passed | Apache-2.0 |
| [Official animatedtiles](#official-animatedtiles) | implemented | passed | Apache-2.0 |
| [Official appchooser](#official-appchooser) | implemented | passed | Apache-2.0 |
| [Official basicdrawing](#official-basicdrawing) | implemented | passed | Apache-2.0 |
| [Official bubbleswidget](#official-bubbleswidget) | implemented | passed | Apache-2.0 |
| [Official chart](#official-chart) | implemented | passed | Apache-2.0 |
| [Official collidingmice](#official-collidingmice) | implemented | passed | Apache-2.0 |
| [Official concentriccircles](#official-concentriccircles) | implemented | passed | Apache-2.0 |
| [Official counterlabel](#official-counterlabel) | implemented | passed | Apache-2.0 |
| [Official delayedencoding](#official-delayedencoding) | implemented | passed | Apache-2.0 |
| [Official designer analogclock](#official-designer-analogclock) | implemented | passed | Apache-2.0 |
| [Official diagramscene](#official-diagramscene) | implemented | passed | Apache-2.0 |
| [Official draganddrop puzzle](#official-draganddrop-puzzle) | implemented | passed | Apache-2.0 |
| [Official dragdroprobot](#official-dragdroprobot) | implemented | passed | Apache-2.0 |
| [Official draggableicons](#official-draggableicons) | implemented | passed | Apache-2.0 |
| [Official easing](#official-easing) | implemented | passed | Apache-2.0 |
| [Official elasticnodes](#official-elasticnodes) | implemented | passed | Apache-2.0 |
| [Official embeddeddialogs](#official-embeddeddialogs) | implemented | passed | Apache-2.0 |
| [Official framecapture](#official-framecapture) | blocked | not run | Apache-2.0 |
| [Official fridgemagnets](#official-fridgemagnets) | implemented | passed | Apache-2.0 |
| [Official grabber](#official-grabber) | blocked | not run | Apache-2.0 |
| [Official hellogl](#official-hellogl) | blocked | not run | Apache-2.0 |
| [Official helloglwidget](#official-helloglwidget) | blocked | not run | Apache-2.0 |
| [Official imageviewer](#official-imageviewer) | implemented | passed | Apache-2.0 |
| [Official itemviews puzzle](#official-itemviews-puzzle) | implemented | passed | Apache-2.0 |
| [Official lighting](#official-lighting) | implemented | passed | Apache-2.0 |
| [Official mandelbrot](#official-mandelbrot) | implemented | passed | Apache-2.0 |
| [Official moveblocks](#official-moveblocks) | implemented | passed | Apache-2.0 |
| [Official openglwindow](#official-openglwindow) | blocked | not run | Apache-2.0 |
| [Official overpainting](#official-overpainting) | blocked | not run | Apache-2.0 |
| [Official padnavigator](#official-padnavigator) | implemented | passed | Apache-2.0 |
| [Official painterpaths](#official-painterpaths) | implemented | passed | Apache-2.0 |
| [Official pixelator](#official-pixelator) | implemented | passed | Apache-2.0 |
| [Official polygonwidget](#official-polygonwidget) | implemented | passed | Apache-2.0 |
| [Official scribble](#official-scribble) | implemented | passed | Apache-2.0 |
| [Official shapedclock](#official-shapedclock) | implemented | passed | Apache-2.0 |
| [Official spreadsheet](#official-spreadsheet) | implemented | passed | Apache-2.0 |
| [Official stardelegate](#official-stardelegate) | implemented | passed | Apache-2.0 |
| [Official states](#official-states) | implemented | passed | Apache-2.0 |
| [Official stickman](#official-stickman) | implemented | passed | Apache-2.0 |
| [Official svgviewer](#official-svgviewer) | implemented | passed | Apache-2.0 |
| [Official tetrix](#official-tetrix) | implemented | passed | Apache-2.0 |
| [Official textobject](#official-textobject) | blocked | not run | Apache-2.0 |
| [Official textures](#official-textures) | blocked | not run | Apache-2.0 |
| [Official tooltips](#official-tooltips) | implemented | passed | Apache-2.0 |
| [Official transformations](#official-transformations) | implemented | passed | Apache-2.0 |
| [Official wiggly](#official-wiggly) | implemented | passed | Apache-2.0 |
| [QtExamples charts/areachart/main](#qtexamples-chartsareachartmain) | blocked | not run | GPL-3.0-only |
| [QtExamples charts/barchart/main](#qtexamples-chartsbarchartmain) | blocked | not run | GPL-3.0-only |
| [QtExamples charts/boxplotchart/main](#qtexamples-chartsboxplotchartmain) | blocked | not run | GPL-3.0-only |
| [QtExamples charts/candlestickchart/main](#qtexamples-chartscandlestickchartmain) | blocked | not run | GPL-3.0-only |
| [QtExamples gui/rasterwindow/main](#qtexamples-guirasterwindowmain) | blocked | not run | GPL-3.0-only |
| [QtExamples qpa/qrasterwindow/main](#qtexamples-qpaqrasterwindowmain) | blocked | not run | GPL-3.0-only |
| [QtExamples qpa/windows/main](#qtexamples-qpawindowsmain) | implemented | passed | GPL-3.0-only |

### Official 2dpainting

- Source: [pyqt/examples / src/pyqt-official/opengl/2dpainting.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/opengl/2dpainting.py)
- Port: [`ports/opengl/pyqt-official/2dpainting-c82d1af7d1a7b0cf.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/opengl/pyqt-official/2dpainting-c82d1af7d1a7b0cf.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("c82d1af7d1a7b0cf")  # inside FontLab
examples.close("c82d1af7d1a7b0cf")
```

### Official analogclock

- Source: [pyqt/examples / src/pyqt-official/widgets/analogclock.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/widgets/analogclock.py)
- Port: [`ports/widgets/pyqt-official/analogclock-d6dc56a5318ffe71.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/widgets/pyqt-official/analogclock-d6dc56a5318ffe71.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("d6dc56a5318ffe71")  # inside FontLab
examples.close("d6dc56a5318ffe71")
```

### Official anchorlayout

- Source: [pyqt/examples / src/pyqt-official/graphicsview/anchorlayout.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/graphicsview/anchorlayout.py)
- Port: [`ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("a96a7978c0b9f6ee")  # inside FontLab
examples.close("a96a7978c0b9f6ee")
```

### Official animatedtiles

- Source: [pyqt/examples / src/pyqt-official/animation/animatedtiles/animatedtiles.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/animation/animatedtiles/animatedtiles.py)
- Port: [`ports/animation/pyqt-official/animatedtiles-1cf57c0f2ac8880a.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/animation/pyqt-official/animatedtiles-1cf57c0f2ac8880a.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("1cf57c0f2ac8880a")  # inside FontLab
examples.close("1cf57c0f2ac8880a")
```

### Official appchooser

- Source: [pyqt/examples / src/pyqt-official/animation/appchooser/appchooser.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/animation/appchooser/appchooser.py)
- Port: [`ports/animation/pyqt-official/appchooser-de30d23621025fe6.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/animation/pyqt-official/appchooser-de30d23621025fe6.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("de30d23621025fe6")  # inside FontLab
examples.close("de30d23621025fe6")
```

### Official basicdrawing

- Source: [pyqt/examples / src/pyqt-official/painting/basicdrawing/basicdrawing.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/painting/basicdrawing/basicdrawing.py)
- Port: [`ports/painting/pyqt-official/basicdrawing-907f39d8bf387501.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/painting/pyqt-official/basicdrawing-907f39d8bf387501.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run01.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("907f39d8bf387501")  # inside FontLab
examples.close("907f39d8bf387501")
```

### Official bubbleswidget

- Source: [pyqt/examples / src/pyqt-official/designer/plugins/widgets/bubbleswidget.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/designer/plugins/widgets/bubbleswidget.py)
- Port: [`ports/designer/pyqt-official/bubbleswidget-9941e3c752b3a3b7.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/designer/pyqt-official/bubbleswidget-9941e3c752b3a3b7.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("9941e3c752b3a3b7")  # inside FontLab
examples.close("9941e3c752b3a3b7")
```

### Official chart

- Source: [pyqt/examples / src/pyqt-official/itemviews/chart/chart.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/itemviews/chart/chart.py)
- Port: [`ports/itemviews/pyqt-official/chart-306c12d5cc1db46c.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/itemviews/pyqt-official/chart-306c12d5cc1db46c.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run01.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("306c12d5cc1db46c")  # inside FontLab
examples.close("306c12d5cc1db46c")
```

### Official collidingmice

- Source: [pyqt/examples / src/pyqt-official/graphicsview/collidingmice/collidingmice.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/graphicsview/collidingmice/collidingmice.py)
- Port: [`ports/graphicsview/pyqt-official/collidingmice-fcfaf9667206bbd6.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphicsview/pyqt-official/collidingmice-fcfaf9667206bbd6.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("fcfaf9667206bbd6")  # inside FontLab
examples.close("fcfaf9667206bbd6")
```

### Official concentriccircles

- Source: [pyqt/examples / src/pyqt-official/painting/concentriccircles.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/painting/concentriccircles.py)
- Port: [`ports/painting/pyqt-official/concentriccircles-912e5c751b20ce97.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/painting/pyqt-official/concentriccircles-912e5c751b20ce97.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("912e5c751b20ce97")  # inside FontLab
examples.close("912e5c751b20ce97")
```

### Official counterlabel

- Source: [pyqt/examples / src/pyqt-official/designer/plugins/widgets/counterlabel.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/designer/plugins/widgets/counterlabel.py)
- Port: [`ports/designer/pyqt-official/counterlabel-1321540b04f33117.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/designer/pyqt-official/counterlabel-1321540b04f33117.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("1321540b04f33117")  # inside FontLab
examples.close("1321540b04f33117")
```

### Official delayedencoding

- Source: [pyqt/examples / src/pyqt-official/draganddrop/delayedencoding/delayedencoding.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/draganddrop/delayedencoding/delayedencoding.py)
- Port: [`ports/draganddrop/pyqt-official/delayedencoding-43c6c2f6f5f036d3.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/draganddrop/pyqt-official/delayedencoding-43c6c2f6f5f036d3.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("43c6c2f6f5f036d3")  # inside FontLab
examples.close("43c6c2f6f5f036d3")
```

### Official designer analogclock

- Source: [pyqt/examples / src/pyqt-official/designer/plugins/widgets/analogclock.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/designer/plugins/widgets/analogclock.py)
- Port: [`ports/designer/pyqt-official/analogclock-4d24cd77c74a8801.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/designer/pyqt-official/analogclock-4d24cd77c74a8801.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("4d24cd77c74a8801")  # inside FontLab
examples.close("4d24cd77c74a8801")
```

### Official diagramscene

- Source: [pyqt/examples / src/pyqt-official/graphicsview/diagramscene/diagramscene.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/graphicsview/diagramscene/diagramscene.py)
- Port: [`ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("1ca857d797199ecf")  # inside FontLab
examples.close("1ca857d797199ecf")
```

### Official draganddrop puzzle

- Source: [pyqt/examples / src/pyqt-official/draganddrop/puzzle/puzzle.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/draganddrop/puzzle/puzzle.py)
- Port: [`ports/draganddrop/pyqt-official/puzzle-c5b4e385cc921da4.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/draganddrop/pyqt-official/puzzle-c5b4e385cc921da4.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run01.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("c5b4e385cc921da4")  # inside FontLab
examples.close("c5b4e385cc921da4")
```

### Official dragdroprobot

- Source: [pyqt/examples / src/pyqt-official/graphicsview/dragdroprobot/dragdroprobot.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/graphicsview/dragdroprobot/dragdroprobot.py)
- Port: [`ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("2cd6ffc2b2ed65bb")  # inside FontLab
examples.close("2cd6ffc2b2ed65bb")
```

### Official draggableicons

- Source: [pyqt/examples / src/pyqt-official/draganddrop/draggableicons/draggableicons.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/draganddrop/draggableicons/draggableicons.py)
- Port: [`ports/draganddrop/pyqt-official/draggableicons-5781fa4ba55c884f.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/draganddrop/pyqt-official/draggableicons-5781fa4ba55c884f.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run01.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("5781fa4ba55c884f")  # inside FontLab
examples.close("5781fa4ba55c884f")
```

### Official easing

- Source: [pyqt/examples / src/pyqt-official/animation/easing/easing.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/animation/easing/easing.py)
- Port: [`ports/animation/pyqt-official/easing-bd6c8feb783ba845.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/animation/pyqt-official/easing-bd6c8feb783ba845.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("bd6c8feb783ba845")  # inside FontLab
examples.close("bd6c8feb783ba845")
```

### Official elasticnodes

- Source: [pyqt/examples / src/pyqt-official/graphicsview/elasticnodes.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/graphicsview/elasticnodes.py)
- Port: [`ports/graphicsview/pyqt-official/elasticnodes-fff97a435b73d548.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphicsview/pyqt-official/elasticnodes-fff97a435b73d548.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("fff97a435b73d548")  # inside FontLab
examples.close("fff97a435b73d548")
```

### Official embeddeddialogs

- Source: [pyqt/examples / src/pyqt-official/graphicsview/embeddeddialogs/embeddeddialogs.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/graphicsview/embeddeddialogs/embeddeddialogs.py)
- Port: [`ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("0578c17977b471f1")  # inside FontLab
examples.close("0578c17977b471f1")
```

### Official framecapture

- Source: [pyqt/examples / src/pyqt-official/webkit/framecapture.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/webkit/framecapture.py)
- Port: [`ports/webkit/pyqt-official/framecapture-ca47b83fbf3f31b9.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/webkit/pyqt-official/framecapture-ca47b83fbf3f31b9.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab.

### Official fridgemagnets

- Source: [pyqt/examples / src/pyqt-official/draganddrop/fridgemagnets/fridgemagnets.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/draganddrop/fridgemagnets/fridgemagnets.py)
- Port: [`ports/draganddrop/pyqt-official/fridgemagnets-da76600eaea7a121.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/draganddrop/pyqt-official/fridgemagnets-da76600eaea7a121.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run01.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("da76600eaea7a121")  # inside FontLab
examples.close("da76600eaea7a121")
```

### Official grabber

- Source: [pyqt/examples / src/pyqt-official/opengl/grabber.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/opengl/grabber.py)
- Port: [`ports/opengl/pyqt-official/grabber-303ea3ee09c4677d.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/opengl/pyqt-official/grabber-303ea3ee09c4677d.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QOpenGLContext.versionFunctions and version-specific GL wrappers are unavailable in FontLab.

### Official hellogl

- Source: [pyqt/examples / src/pyqt-official/opengl/hellogl.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/opengl/hellogl.py)
- Port: [`ports/opengl/pyqt-official/hellogl-1ad60855ca28f3cc.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/opengl/pyqt-official/hellogl-1ad60855ca28f3cc.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QOpenGLContext.versionFunctions and version-specific GL wrappers are unavailable in FontLab.

### Official helloglwidget

- Source: [pyqt/examples / src/pyqt-official/designer/plugins/widgets/helloglwidget.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/designer/plugins/widgets/helloglwidget.py)
- Port: [`ports/designer/pyqt-official/helloglwidget-5941e31267112c98.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/designer/pyqt-official/helloglwidget-5941e31267112c98.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QOpenGLContext.versionFunctions and version-specific OpenGL function wrappers are unavailable

### Official imageviewer

- Source: [pyqt/examples / src/pyqt-official/widgets/imageviewer.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/widgets/imageviewer.py)
- Port: [`ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("16456ba02f4b79cc")  # inside FontLab
examples.close("16456ba02f4b79cc")
```

### Official itemviews puzzle

- Source: [pyqt/examples / src/pyqt-official/itemviews/puzzle/puzzle.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/itemviews/puzzle/puzzle.py)
- Port: [`ports/itemviews/pyqt-official/puzzle-878fe9f714df3b5e.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/itemviews/pyqt-official/puzzle-878fe9f714df3b5e.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run01.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("878fe9f714df3b5e")  # inside FontLab
examples.close("878fe9f714df3b5e")
```

### Official lighting

- Source: [pyqt/examples / src/pyqt-official/effects/lighting.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/effects/lighting.py)
- Port: [`ports/effects/pyqt-official/lighting-b823a76f79197d84.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/effects/pyqt-official/lighting-b823a76f79197d84.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run01.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("b823a76f79197d84")  # inside FontLab
examples.close("b823a76f79197d84")
```

### Official mandelbrot

- Source: [pyqt/examples / src/pyqt-official/threads/mandelbrot.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/threads/mandelbrot.py)
- Port: [`ports/threads/pyqt-official/mandelbrot-0788354954c8e613.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/threads/pyqt-official/mandelbrot-0788354954c8e613.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("0788354954c8e613")  # inside FontLab
examples.close("0788354954c8e613")
```

### Official moveblocks

- Source: [pyqt/examples / src/pyqt-official/animation/moveblocks.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/animation/moveblocks.py)
- Port: [`ports/animation/pyqt-official/moveblocks-b7283d74afb78218.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/animation/pyqt-official/moveblocks-b7283d74afb78218.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("b7283d74afb78218")  # inside FontLab
examples.close("b7283d74afb78218")
```

### Official openglwindow

- Source: [pyqt/examples / src/pyqt-official/opengl/openglwindow.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/opengl/openglwindow.py)
- Port: [`ports/opengl/pyqt-official/openglwindow-b383fecf912548bb.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/opengl/pyqt-official/openglwindow-b383fecf912548bb.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QOpenGLContext.versionFunctions and version-specific GL wrappers are unavailable in FontLab.

### Official overpainting

- Source: [pyqt/examples / src/pyqt-official/opengl/overpainting.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/opengl/overpainting.py)
- Port: [`ports/opengl/pyqt-official/overpainting-fcada4fff6524fcf.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/opengl/pyqt-official/overpainting-fcada4fff6524fcf.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QOpenGLContext.versionFunctions and version-specific GL wrappers are unavailable in FontLab.

### Official padnavigator

- Source: [pyqt/examples / src/pyqt-official/graphicsview/padnavigator/padnavigator.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/graphicsview/padnavigator/padnavigator.py)
- Port: [`ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("a58650b5461c0f48")  # inside FontLab
examples.close("a58650b5461c0f48")
```

### Official painterpaths

- Source: [pyqt/examples / src/pyqt-official/painting/painterpaths.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/painting/painterpaths.py)
- Port: [`ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("13a6bb9a9d2b9037")  # inside FontLab
examples.close("13a6bb9a9d2b9037")
```

### Official pixelator

- Source: [pyqt/examples / src/pyqt-official/itemviews/pixelator/pixelator.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/itemviews/pixelator/pixelator.py)
- Port: [`ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("d50ad6638357e669")  # inside FontLab
examples.close("d50ad6638357e669")
```

### Official polygonwidget

- Source: [pyqt/examples / src/pyqt-official/designer/plugins/widgets/polygonwidget.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/designer/plugins/widgets/polygonwidget.py)
- Port: [`ports/designer/pyqt-official/polygonwidget-773db5c24ae98ffb.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/designer/pyqt-official/polygonwidget-773db5c24ae98ffb.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("773db5c24ae98ffb")  # inside FontLab
examples.close("773db5c24ae98ffb")
```

### Official scribble

- Source: [pyqt/examples / src/pyqt-official/widgets/scribble.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/widgets/scribble.py)
- Port: [`ports/widgets/pyqt-official/scribble-8e5aa13798c2763c.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/widgets/pyqt-official/scribble-8e5aa13798c2763c.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("8e5aa13798c2763c")  # inside FontLab
examples.close("8e5aa13798c2763c")
```

### Official shapedclock

- Source: [pyqt/examples / src/pyqt-official/widgets/shapedclock.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/widgets/shapedclock.py)
- Port: [`ports/widgets/pyqt-official/shapedclock-248e64416b9b218c.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/widgets/pyqt-official/shapedclock-248e64416b9b218c.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("248e64416b9b218c")  # inside FontLab
examples.close("248e64416b9b218c")
```

### Official spreadsheet

- Source: [pyqt/examples / src/pyqt-official/itemviews/spreadsheet/spreadsheet.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/itemviews/spreadsheet/spreadsheet.py)
- Port: [`ports/itemviews/pyqt-official/spreadsheet-bf3b39a8c2df8e94.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/itemviews/pyqt-official/spreadsheet-bf3b39a8c2df8e94.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("bf3b39a8c2df8e94")  # inside FontLab
examples.close("bf3b39a8c2df8e94")
```

### Official stardelegate

- Source: [pyqt/examples / src/pyqt-official/itemviews/stardelegate.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/itemviews/stardelegate.py)
- Port: [`ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("dc59f268ee01e364")  # inside FontLab
examples.close("dc59f268ee01e364")
```

### Official states

- Source: [pyqt/examples / src/pyqt-official/animation/states/states.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/animation/states/states.py)
- Port: [`ports/animation/pyqt-official/states-29f6a7d0a3bb6813.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/animation/pyqt-official/states-29f6a7d0a3bb6813.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("29f6a7d0a3bb6813")  # inside FontLab
examples.close("29f6a7d0a3bb6813")
```

### Official stickman

- Source: [pyqt/examples / src/pyqt-official/animation/stickman/stickman.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/animation/stickman/stickman.py)
- Port: [`ports/animation/pyqt-official/stickman-243ae486f9528e8c.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/animation/pyqt-official/stickman-243ae486f9528e8c.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("243ae486f9528e8c")  # inside FontLab
examples.close("243ae486f9528e8c")
```

### Official svgviewer

- Source: [pyqt/examples / src/pyqt-official/painting/svgviewer/svgviewer.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/painting/svgviewer/svgviewer.py)
- Port: [`ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("b2d717e4d43806d2")  # inside FontLab
examples.close("b2d717e4d43806d2")
```

### Official tetrix

- Source: [pyqt/examples / src/pyqt-official/widgets/tetrix.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/widgets/tetrix.py)
- Port: [`ports/widgets/pyqt-official/tetrix-e63bffc17abf2fde.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/widgets/pyqt-official/tetrix-e63bffc17abf2fde.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("e63bffc17abf2fde")  # inside FontLab
examples.close("e63bffc17abf2fde")
```

### Official textobject

- Source: [pyqt/examples / src/pyqt-official/richtext/textobject/textobject.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/richtext/textobject/textobject.py)
- Port: [`ports/richtext/pyqt-official/textobject-806fd814a2ea4d46.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/richtext/pyqt-official/textobject-806fd814a2ea4d46.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QTextObjectInterface is unavailable in FontLab.

### Official textures

- Source: [pyqt/examples / src/pyqt-official/opengl/textures/textures.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/opengl/textures/textures.py)
- Port: [`ports/opengl/pyqt-official/textures-ed6d42d4faa7e0bb.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/opengl/pyqt-official/textures-ed6d42d4faa7e0bb.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QOpenGLContext.versionFunctions and version-specific GL wrappers are unavailable in FontLab.

### Official tooltips

- Source: [pyqt/examples / src/pyqt-official/widgets/tooltips/tooltips.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/widgets/tooltips/tooltips.py)
- Port: [`ports/widgets/pyqt-official/tooltips-e62ce3eb648cfb4c.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/widgets/pyqt-official/tooltips-e62ce3eb648cfb4c.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run01.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("e62ce3eb648cfb4c")  # inside FontLab
examples.close("e62ce3eb648cfb4c")
```

### Official transformations

- Source: [pyqt/examples / src/pyqt-official/painting/transformations.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/painting/transformations.py)
- Port: [`ports/painting/pyqt-official/transformations-c12a2071adbab88b.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/painting/pyqt-official/transformations-c12a2071adbab88b.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("c12a2071adbab88b")  # inside FontLab
examples.close("c12a2071adbab88b")
```

### Official wiggly

- Source: [pyqt/examples / src/pyqt-official/widgets/wiggly.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/widgets/wiggly.py)
- Port: [`ports/widgets/pyqt-official/wiggly-509e781f1267967f.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/widgets/pyqt-official/wiggly-509e781f1267967f.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run03.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("509e781f1267967f")  # inside FontLab
examples.close("509e781f1267967f")
```

### QtExamples charts/areachart/main

- Source: [eyllanesc/QtExamples / official/charts/areachart/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/charts/areachart/main.py)
- Port: [`ports/graphics-painting/eyllanesc/main-93131a29a3b71ea3.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphics-painting/eyllanesc/main-93131a29a3b71ea3.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtCharts (QtChart); required native APIs: QAreaSeries, QChart, QChartView, QLineSeries. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.

### QtExamples charts/barchart/main

- Source: [eyllanesc/QtExamples / official/charts/barchart/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/charts/barchart/main.py)
- Port: [`ports/graphics-painting/eyllanesc/main-9fed8c2f3765272b.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphics-painting/eyllanesc/main-9fed8c2f3765272b.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtCharts (QtChart); required native APIs: QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QValueAxis. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.

### QtExamples charts/boxplotchart/main

- Source: [eyllanesc/QtExamples / official/charts/boxplotchart/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/charts/boxplotchart/main.py)
- Port: [`ports/graphics-painting/eyllanesc/main-f9107c0d26ffc4aa.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphics-painting/eyllanesc/main-f9107c0d26ffc4aa.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtCharts (QtChart); required native APIs: QBoxPlotSeries, QBoxSet, QChart, QChartView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.

### QtExamples charts/candlestickchart/main

- Source: [eyllanesc/QtExamples / official/charts/candlestickchart/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/charts/candlestickchart/main.py)
- Port: [`ports/graphics-painting/eyllanesc/main-032d404c69db6baa.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphics-painting/eyllanesc/main-032d404c69db6baa.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtCharts (QtChart); required native APIs: QCandlestickSeries, QCandlestickSet, QChart, QChartView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.

### QtExamples gui/rasterwindow/main

- Source: [eyllanesc/QtExamples / official/gui/rasterwindow/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/gui/rasterwindow/main.py)
- Port: [`ports/graphics-painting/eyllanesc/main-3525151ac8d550f5.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphics-painting/eyllanesc/main-3525151ac8d550f5.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt.QtGui.QGradient lacks the NightFade preset and its preset constructor overload, required by RasterWindow.renderNow for its exact background. QWindow/QBackingStore exist, but a replacement gradient is not supplied.

### QtExamples qpa/qrasterwindow/main

- Source: [eyllanesc/QtExamples / official/qpa/qrasterwindow/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/qpa/qrasterwindow/main.py)
- Port: [`ports/graphics-painting/eyllanesc/main-0b7e380ab45addbd.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphics-painting/eyllanesc/main-0b7e380ab45addbd.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt.QtGui.QMatrix4x4 exposes neither __mul__ nor a matrix-product method. PaintedWindow.paintEvent requires projection * view * model; wrapper arithmetic is forbidden in FontLab. QRasterWindow exists, but numeric matrix replacement is not implemented.

### QtExamples qpa/windows/main

- Source: [eyllanesc/QtExamples / official/qpa/windows/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/qpa/windows/main.py)
- Port: [`ports/graphics-painting/eyllanesc/main-b1c25455dbcb6bac.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/graphics-painting/eyllanesc/main-b1c25455dbcb6bac.py)
- Implementation: **implemented**
- Native acceptance: passed (historical record; workspace evidence `examples-interactions/native-lic-final2.jsonl`)
- Licence: GPL-3.0-only

```python
import fontlab_python_examples as examples

handle = examples.launch("b1c25455dbcb6bac")  # inside FontLab
examples.close("b1c25455dbcb6bac")
```
