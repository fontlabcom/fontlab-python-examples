# Examples: multimedia

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

9 records: 1 implemented, 8 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [Official audiodevices](#official-audiodevices) | blocked | not run | Apache-2.0 |
| [Official audiooutput](#official-audiooutput) | blocked | not run | Apache-2.0 |
| [Official camera](#official-camera) | blocked | not run | Apache-2.0 |
| [Official player](#official-player) | blocked | not run | Apache-2.0 |
| [Official videographicsitem](#official-videographicsitem) | blocked | not run | Apache-2.0 |
| [Official videowidget](#official-videowidget) | blocked | not run | Apache-2.0 |
| [QPainter](#qpainter) | implemented | passed | MIT |
| [QtExamples charts/audio/main](#qtexamples-chartsaudiomain) | blocked | not run | GPL-3.0-only |
| [QtExamples multimedia/audiodevices/main](#qtexamples-multimediaaudiodevicesmain) | blocked | not run | GPL-3.0-only |

### Official audiodevices

- Source: [pyqt/examples / src/pyqt-official/multimedia/audiodevices/audiodevices.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/multimedia/audiodevices/audiodevices.py)
- Port: [`ports/multimedia/pyqt-official/audiodevices-74af8d8d2d7774b8.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/multimedia/pyqt-official/audiodevices-74af8d8d2d7774b8.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtMultimedia audio bindings are unavailable in FontLab.

### Official audiooutput

- Source: [pyqt/examples / src/pyqt-official/multimedia/audiooutput.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/multimedia/audiooutput.py)
- Port: [`ports/multimedia/pyqt-official/audiooutput-c391afd8516131e1.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/multimedia/pyqt-official/audiooutput-c391afd8516131e1.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtMultimedia audio bindings are unavailable in FontLab.

### Official camera

- Source: [pyqt/examples / src/pyqt-official/multimediawidgets/camera/camera.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/multimediawidgets/camera/camera.py)
- Port: [`ports/multimediawidgets/pyqt-official/camera-f6d352360ae9bdfb.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/multimediawidgets/pyqt-official/camera-f6d352360ae9bdfb.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtMultimedia and QtMultimediaWidgets media bindings are unavailable in FontLab.

### Official player

- Source: [pyqt/examples / src/pyqt-official/multimediawidgets/player.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/multimediawidgets/player.py)
- Port: [`ports/multimediawidgets/pyqt-official/player-5eb4b9eaa2d5c9dc.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/multimediawidgets/pyqt-official/player-5eb4b9eaa2d5c9dc.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtMultimedia and QtMultimediaWidgets media bindings are unavailable in FontLab.

### Official videographicsitem

- Source: [pyqt/examples / src/pyqt-official/multimediawidgets/videographicsitem.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/multimediawidgets/videographicsitem.py)
- Port: [`ports/multimediawidgets/pyqt-official/videographicsitem-a57a89e523c75b7f.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/multimediawidgets/pyqt-official/videographicsitem-a57a89e523c75b7f.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtMultimedia and QtMultimediaWidgets media bindings are unavailable in FontLab.

### Official videowidget

- Source: [pyqt/examples / src/pyqt-official/multimediawidgets/videowidget.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/multimediawidgets/videowidget.py)
- Port: [`ports/multimediawidgets/pyqt-official/videowidget-481c128fba3a714b.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/multimediawidgets/pyqt-official/videowidget-481c128fba3a714b.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtMultimedia and QtMultimediaWidgets media bindings are unavailable in FontLab.

### QPainter

- Source: [pyqt/examples / src/10 QPainter Python example/main.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/10%20QPainter%20Python%20example/main.py)
- Port: [`ports/multimedia/pyqt-examples/main-1151b1cb878f192a.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/multimedia/pyqt-examples/main-1151b1cb878f192a.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `b9ead3f`; workspace evidence `examples-resources/acceptance02.jsonl`)
- Licence: MIT

```python
import fontlab_python_examples as examples

handle = examples.launch("1151b1cb878f192a")  # inside FontLab
examples.close("1151b1cb878f192a")
```

### QtExamples charts/audio/main

- Source: [eyllanesc/QtExamples / official/charts/audio/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/charts/audio/main.py)
- Port: [`ports/multimedia/eyllanesc/main-e1c73422208670cb.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/multimedia/eyllanesc/main-e1c73422208670cb.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtCharts (QtChart); required native APIs: QChart, QChartView, QLineSeries, QValueAxis, QXYSeries. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.

### QtExamples multimedia/audiodevices/main

- Source: [eyllanesc/QtExamples / official/multimedia/audiodevices/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/multimedia/audiodevices/main.py)
- Port: [`ports/multimedia/eyllanesc/main-307534c4e8e2211c.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/multimedia/eyllanesc/main-307534c4e8e2211c.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QAudio, QAudioDeviceInfo, QAudioFormat. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.
