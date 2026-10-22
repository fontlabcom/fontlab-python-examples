# Examples: gstreamer

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

1 records: 0 implemented, 1 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [QtExamples gst_pipeline/main](#qtexamples-gst_pipelinemain) | blocked | not run | GPL-3.0-only |

### QtExamples gst_pipeline/main

- Source: [eyllanesc/QtExamples / others/gst_pipeline/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/gst_pipeline/main.py)
- Port: [`ports/gstreamer/eyllanesc/main-a0ac1b252a14609e.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/gstreamer/eyllanesc/main-a0ac1b252a14609e.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QMediaContent, QMediaPlayer, QVideoWidget. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. The Qt GStreamer pipeline player/video sink is also unavailable.
