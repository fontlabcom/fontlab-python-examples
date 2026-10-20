# Examples: network

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, now preserved under `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

24 records: 17 implemented, 7 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [Official blockingfortuneclient](#official-blockingfortuneclient) | implemented | passed | Apache-2.0 |
| [Official broadcastreceiver](#official-broadcastreceiver) | implemented | passed | Apache-2.0 |
| [Official broadcastsender](#official-broadcastsender) | implemented | passed | Apache-2.0 |
| [Official domtraversal](#official-domtraversal) | blocked | not run | Apache-2.0 |
| [Official fancybrowser](#official-fancybrowser) | blocked | not run | Apache-2.0 |
| [Official fortuneclient](#official-fortuneclient) | implemented | passed | Apache-2.0 |
| [Official fortuneserver](#official-fortuneserver) | implemented | passed | Apache-2.0 |
| [Official http](#official-http) | implemented | passed | Apache-2.0 |
| [Official lightmaps](#official-lightmaps) | implemented | passed | Apache-2.0 |
| [Official localfortuneclient](#official-localfortuneclient) | implemented | passed | Apache-2.0 |
| [Official localfortuneserver](#official-localfortuneserver) | implemented | passed | Apache-2.0 |
| [Official loopback](#official-loopback) | implemented | passed | Apache-2.0 |
| [Official previewer](#official-previewer) | blocked | not run | Apache-2.0 |
| [Official simpleselector](#official-simpleselector) | blocked | not run | Apache-2.0 |
| [Official stylesheet](#official-stylesheet) | implemented | passed | Apache-2.0 |
| [Official threadedfortuneserver](#official-threadedfortuneserver) | implemented | passed | Apache-2.0 |
| [PyQt Thread 01_single_threaded](#pyqt-thread-01_single_threaded) | implemented | passed | MIT |
| [PyQt Thread 02_multithreaded](#pyqt-thread-02_multithreaded) | implemented | passed | MIT |
| [PyQt Thread 03_with_threadutil](#pyqt-thread-03_with_threadutil) | implemented | passed | MIT |
| [QtExamples customcompleter/google_search](#qtexamples-customcompletergoogle_search) | implemented | passed | GPL-3.0-only |
| [QtExamples multimedia/audiodevices/audiodevicesbase_ui](#qtexamples-multimediaaudiodevicesaudiodevicesbase_ui) | blocked | not run | GPL-3.0-only |
| [QtExamples network/googlesuggest/main](#qtexamples-networkgooglesuggestmain) | blocked | not run | GPL-3.0-only |
| [QtExamples network/loopback/main](#qtexamples-networkloopbackmain) | implemented | passed | GPL-3.0-only |
| [QtExamples websockets/sslechoserver/main](#qtexamples-websocketssslechoservermain) | blocked | not run | GPL-3.0-only |

### Official blockingfortuneclient

- Source: [pyqt/examples / src/pyqt-official/network/blockingfortuneclient.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/network/blockingfortuneclient.py)
- Port: [`ports/network/pyqt-official/blockingfortuneclient-79f3a23172968ad2.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-official/blockingfortuneclient-79f3a23172968ad2.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("79f3a23172968ad2")  # inside FontLab
examples.close("79f3a23172968ad2")
```

### Official broadcastreceiver

- Source: [pyqt/examples / src/pyqt-official/network/broadcastreceiver.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/network/broadcastreceiver.py)
- Port: [`ports/network/pyqt-official/broadcastreceiver-0bba8a80541ab04f.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-official/broadcastreceiver-0bba8a80541ab04f.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("0bba8a80541ab04f")  # inside FontLab
examples.close("0bba8a80541ab04f")
```

### Official broadcastsender

- Source: [pyqt/examples / src/pyqt-official/network/broadcastsender.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/network/broadcastsender.py)
- Port: [`ports/network/pyqt-official/broadcastsender-90721289b8108c4f.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-official/broadcastsender-90721289b8108c4f.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("90721289b8108c4f")  # inside FontLab
examples.close("90721289b8108c4f")
```

### Official domtraversal

- Source: [pyqt/examples / src/pyqt-official/webkit/domtraversal/domtraversal.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/webkit/domtraversal/domtraversal.py)
- Port: [`ports/webkit/pyqt-official/domtraversal-8d5ea81a74e30222.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/webkit/pyqt-official/domtraversal-8d5ea81a74e30222.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab.

### Official fancybrowser

- Source: [pyqt/examples / src/pyqt-official/webkit/fancybrowser/fancybrowser.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/webkit/fancybrowser/fancybrowser.py)
- Port: [`ports/webkit/pyqt-official/fancybrowser-f4000cf8ca288375.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/webkit/pyqt-official/fancybrowser-f4000cf8ca288375.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab.

### Official fortuneclient

- Source: [pyqt/examples / src/pyqt-official/network/fortuneclient.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/network/fortuneclient.py)
- Port: [`ports/network/pyqt-official/fortuneclient-fbb4e3c7288fed7c.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-official/fortuneclient-fbb4e3c7288fed7c.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("fbb4e3c7288fed7c")  # inside FontLab
examples.close("fbb4e3c7288fed7c")
```

### Official fortuneserver

- Source: [pyqt/examples / src/pyqt-official/network/fortuneserver.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/network/fortuneserver.py)
- Port: [`ports/network/pyqt-official/fortuneserver-aad57160cfd51894.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-official/fortuneserver-aad57160cfd51894.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("aad57160cfd51894")  # inside FontLab
examples.close("aad57160cfd51894")
```

### Official http

- Source: [pyqt/examples / src/pyqt-official/network/http/http.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/network/http/http.py)
- Port: [`ports/network/pyqt-official/http-409f3d46a9555f23.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-official/http-409f3d46a9555f23.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("409f3d46a9555f23")  # inside FontLab
examples.close("409f3d46a9555f23")
```

### Official lightmaps

- Source: [pyqt/examples / src/pyqt-official/network/lightmaps.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/network/lightmaps.py)
- Port: [`ports/network/pyqt-official/lightmaps-d8803c2afaabf3d5.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-official/lightmaps-d8803c2afaabf3d5.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("d8803c2afaabf3d5")  # inside FontLab
examples.close("d8803c2afaabf3d5")
```

### Official localfortuneclient

- Source: [pyqt/examples / src/pyqt-official/ipc/localfortuneclient.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/ipc/localfortuneclient.py)
- Port: [`ports/ipc/pyqt-official/localfortuneclient-0ad3432ccdca7ac0.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/ipc/pyqt-official/localfortuneclient-0ad3432ccdca7ac0.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("0ad3432ccdca7ac0")  # inside FontLab
examples.close("0ad3432ccdca7ac0")
```

### Official localfortuneserver

- Source: [pyqt/examples / src/pyqt-official/ipc/localfortuneserver.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/ipc/localfortuneserver.py)
- Port: [`ports/ipc/pyqt-official/localfortuneserver-a14d08fe23965bec.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/ipc/pyqt-official/localfortuneserver-a14d08fe23965bec.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("a14d08fe23965bec")  # inside FontLab
examples.close("a14d08fe23965bec")
```

### Official loopback

- Source: [pyqt/examples / src/pyqt-official/network/loopback.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/network/loopback.py)
- Port: [`ports/network/pyqt-official/loopback-ebf87d5f5390b0fd.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-official/loopback-ebf87d5f5390b0fd.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("ebf87d5f5390b0fd")  # inside FontLab
examples.close("ebf87d5f5390b0fd")
```

### Official previewer

- Source: [pyqt/examples / src/pyqt-official/webkit/previewer/previewer.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/webkit/previewer/previewer.py)
- Port: [`ports/webkit/pyqt-official/previewer-47298251b3c83ecf.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/webkit/pyqt-official/previewer-47298251b3c83ecf.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab.

### Official simpleselector

- Source: [pyqt/examples / src/pyqt-official/webkit/simpleselector/simpleselector.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/webkit/simpleselector/simpleselector.py)
- Port: [`ports/webkit/pyqt-official/simpleselector-ae16288fede27692.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/webkit/pyqt-official/simpleselector-ae16288fede27692.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtWebKit and QtWebKitWidgets DOM bindings are unavailable in FontLab.

### Official stylesheet

- Source: [pyqt/examples / src/pyqt-official/widgets/stylesheet/stylesheet.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/widgets/stylesheet/stylesheet.py)
- Port: [`ports/widgets/pyqt-official/stylesheet-876eab33b6a99e31.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/widgets/pyqt-official/stylesheet-876eab33b6a99e31.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run01.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("876eab33b6a99e31")  # inside FontLab
examples.close("876eab33b6a99e31")
```

### Official threadedfortuneserver

- Source: [pyqt/examples / src/pyqt-official/network/threadedfortuneserver.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/network/threadedfortuneserver.py)
- Port: [`ports/network/pyqt-official/threadedfortuneserver-98f207907001ce47.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-official/threadedfortuneserver-98f207907001ce47.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run06.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("98f207907001ce47")  # inside FontLab
examples.close("98f207907001ce47")
```

### PyQt Thread 01_single_threaded

- Source: [pyqt/examples / src/11 PyQt Thread example/01_single_threaded.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/11%20PyQt%20Thread%20example/01_single_threaded.py)
- Port: [`ports/network/pyqt-examples/01-single-threaded-1e79bddb6d52574d.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-examples/01-single-threaded-1e79bddb6d52574d.py)
- Implementation: **implemented**
- Native acceptance: passed (historical record; workspace evidence `examples-interactions/native-lic-final2.jsonl`)
- Licence: MIT

```python
import fontlab_python_examples as examples

handle = examples.launch("1e79bddb6d52574d")  # inside FontLab
examples.close("1e79bddb6d52574d")
```

### PyQt Thread 02_multithreaded

- Source: [pyqt/examples / src/11 PyQt Thread example/02_multithreaded.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/11%20PyQt%20Thread%20example/02_multithreaded.py)
- Port: [`ports/network/pyqt-examples/02-multithreaded-88fa78cafb505cfa.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-examples/02-multithreaded-88fa78cafb505cfa.py)
- Implementation: **implemented**
- Native acceptance: passed (historical record; workspace evidence `examples-interactions/native-lic-final2.jsonl`)
- Licence: MIT

```python
import fontlab_python_examples as examples

handle = examples.launch("88fa78cafb505cfa")  # inside FontLab
examples.close("88fa78cafb505cfa")
```

### PyQt Thread 03_with_threadutil

- Source: [pyqt/examples / src/11 PyQt Thread example/03_with_threadutil.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/11%20PyQt%20Thread%20example/03_with_threadutil.py)
- Port: [`ports/network/pyqt-examples/03-with-threadutil-83bc55d45ae367d0.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/pyqt-examples/03-with-threadutil-83bc55d45ae367d0.py)
- Implementation: **implemented**
- Native acceptance: passed (historical record; workspace evidence `examples-interactions/native-lic-final2.jsonl`)
- Licence: MIT

```python
import fontlab_python_examples as examples

handle = examples.launch("83bc55d45ae367d0")  # inside FontLab
examples.close("83bc55d45ae367d0")
```

### QtExamples customcompleter/google_search

- Source: [eyllanesc/QtExamples / others/customcompleter/google_search.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/customcompleter/google_search.py)
- Port: [`ports/network/eyllanesc/google-search-edeef5f840c20e15.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/eyllanesc/google-search-edeef5f840c20e15.py)
- Implementation: **implemented**
- Native acceptance: passed (historical record; workspace evidence `examples-interactions/native-lic-final2.jsonl`)
- Licence: GPL-3.0-only

```python
import fontlab_python_examples as examples

handle = examples.launch("edeef5f840c20e15")  # inside FontLab
examples.close("edeef5f840c20e15")
```

### QtExamples multimedia/audiodevices/audiodevicesbase_ui

- Source: [eyllanesc/QtExamples / official/multimedia/audiodevices/audiodevicesbase_ui.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/multimedia/audiodevices/audiodevicesbase_ui.py)
- Port: [`ports/network/eyllanesc/audiodevicesbase-ui-0d72445fb116793d.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/eyllanesc/audiodevicesbase-ui-0d72445fb116793d.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QAudio, QAudioDeviceInfo, QAudioFormat. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.

### QtExamples network/googlesuggest/main

- Source: [eyllanesc/QtExamples / official/network/googlesuggest/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/network/googlesuggest/main.py)
- Port: [`ports/network/eyllanesc/main-eea833917398267a.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/eyllanesc/main-eea833917398267a.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt.QtCore has no QXmlStreamReader, required by GSuggestCompletion.handleNetworkData to parse suggestions. A stdlib XML parser plus owned localhost suggestion/search server is a possible behavior-preserving future adaptation; this record does not claim that substitution is implemented.

### QtExamples network/loopback/main

- Source: [eyllanesc/QtExamples / official/network/loopback/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/network/loopback/main.py)
- Port: [`ports/network/eyllanesc/main-ecc2e23449331df1.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/eyllanesc/main-ecc2e23449331df1.py)
- Implementation: **implemented**
- Native acceptance: passed (historical record; workspace evidence `examples-interactions/native-lic-final2.jsonl`)
- Licence: GPL-3.0-only

```python
import fontlab_python_examples as examples

handle = examples.launch("ecc2e23449331df1")  # inside FontLab
examples.close("ecc2e23449331df1")
```

### QtExamples websockets/sslechoserver/main

- Source: [eyllanesc/QtExamples / official/websockets/sslechoserver/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/websockets/sslechoserver/main.py)
- Port: [`ports/network/eyllanesc/main-768c423bdd1fa074.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/network/eyllanesc/main-768c423bdd1fa074.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtWebSockets; required native APIs: QWebSocketServer. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.
