# Examples: video-overlay

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

2 records: 0 implemented, 2 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [QtExamples not_classified/1/main](#qtexamples-not_classified1main) | blocked | not run | GPL-3.0-only |
| [QtExamples qmlvideoviewer/main](#qtexamples-qmlvideoviewermain) | blocked | not run | GPL-3.0-only |

### QtExamples not_classified/1/main

- Source: [eyllanesc/QtExamples / others/not_classified/1/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/not_classified/1/main.py)
- Port: [`ports/video-overlay/eyllanesc/main-b3c5b8f7bcf09a1d.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/video-overlay/eyllanesc/main-b3c5b8f7bcf09a1d.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QGraphicsVideoItem, QMediaContent, QMediaPlayer. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.

### QtExamples qmlvideoviewer/main

- Source: [eyllanesc/QtExamples / others/qmlvideoviewer/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/qmlvideoviewer/main.py)
- Port: [`ports/video-overlay/eyllanesc/main-e9392311a500d3dd.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/video-overlay/eyllanesc/main-e9392311a500d3dd.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtQml / QtMultimedia; required native APIs: QAbstractVideoBuffer, QAbstractVideoFilter, QAbstractVideoSurface, QQmlApplicationEngine, QVideoFilterRunnable, QVideoFrame, QVideoSurfaceFormat, qmlRegisterType. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.
