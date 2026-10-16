# this_file: ports/network/eyllanesc/google-search-edeef5f840c20e15.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: others/customcompleter/google_search.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-


import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.official import Demo, LocalHttp, read


def build(qt: Any) -> ExampleHandle:
    demo = Demo(qt, __file__, "edeef5f840c20e15")
    gui, core, network = qt.QtGui, qt.QtCore, qt.QtNetwork
    window = gui.QLineEdit()
    demo.begin(window)
    try:
        window.setWindowTitle("Google search suggestions (owned peer)")
        window.resize(640, 60)
        completer = demo.remember("completer", gui.QCompleter(window))
        completer.setCaseSensitivity(core.Qt.CaseInsensitive)
        model = demo.remember("model", gui.QStandardItemModel(window))
        completer.setModel(model)
        window.setCompleter(completer)
        manager = demo.remember("networkManager", network.QNetworkAccessManager(window))
        state = {"query": "", "suggestions": [], "pending": False}
        current = [None]

        def respond(method: str, path: str, body: bytes) -> tuple[bytes, str]:
            if method != "GET" or urlsplit(path).path != "/complete/search":
                raise ValueError("Unknown owned suggestion request")
            query = parse_qs(urlsplit(path).query).get("q", [""])[0]
            document = ET.Element("toplevel")
            for text in [query, query + " PythonQt", query + " FontLab"]:
                completion = ET.SubElement(document, "CompleteSuggestion")
                ET.SubElement(completion, "suggestion", data=text)
            return ET.tostring(document, encoding="utf-8"), "application/xml"

        server = LocalHttp(demo, respond)
        timer = demo.remember("suggestTimer", core.QTimer(window))
        timer.setSingleShot(True)
        deadline = demo.remember("requestTimer", core.QTimer(window))
        deadline.setSingleShot(True)
        demo.handle.cleanup.extend([timer.stop, deadline.stop])

        def dispose() -> None:
            reply = current[0]
            if reply is not None:
                current[0] = None
                demo.forget(reply)
                reply.abort()
                reply.deleteLater()
            state["pending"] = False
            deadline.stop()

        def finished() -> None:
            reply = current[0]
            if reply is None:
                return
            try:
                if reply.error():
                    raise OSError(str(reply.errorString()))
                if reply.attribute(network.QNetworkRequest.RedirectionTargetAttribute):
                    raise ValueError("Owned suggestion redirects are refused")
                document = ET.fromstring(reply.readAll().data())
                results = [node.attrib["data"] for node in document.iter("suggestion")]
                model.clear()
                for text in results:
                    model.appendRow(gui.QStandardItem(text))
                state["suggestions"] = results
                demo.error = ""
                completer.setCompletionPrefix(state["query"])
                completer.complete()
            except (OSError, ValueError, KeyError, ET.ParseError) as error:
                demo.error = str(error)
            finally:
                dispose()

        def search() -> None:
            dispose()
            model.clear()
            state.update(query=str(read(window, "text")).strip(), suggestions=[])
            if not state["query"]:
                return
            request = network.QNetworkRequest(
                core.QUrl(
                    server.url("/complete/search?")
                    + urlencode({"q": state["query"], "output": "toolbar", "hl": "en"})
                )
            )
            request.setAttribute(
                network.QNetworkRequest.FollowRedirectsAttribute, False
            )
            current[0] = manager.get(request)
            state["pending"] = True
            demo.connect(current[0], "finished()", finished)
            deadline.start(2000)

        def timed_out() -> None:
            demo.error = "Owned suggestion request timed out"
            dispose()

        demo.connect(window, "textEdited(QString)", lambda: timer.start(250))
        demo.connect(timer, "timeout()", search)
        demo.connect(deadline, "timeout()", timed_out)
        demo.handle.cleanup.append(dispose)
        demo.remember("search", search)
        return demo.finish(
            window,
            lambda: {
                **state,
                "suggestions": list(state["suggestions"]),
                "text": str(read(window, "text")),
                "row_count": int(model.rowCount()),
                "endpoint": server.url("/complete/search"),
                "owned_endpoint": True,
            },
        )
    except BaseException:
        demo.abort()
        raise


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("edeef5f840c20e15")
