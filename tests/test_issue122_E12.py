# this_file: tests/test_issue122_E12.py
"""Audit network, declarative, media and launcher retirement identities.

Read preserved files as data only. Never import or execute the examples.
The frozen inventory, file hashes and native metadata constrain the report.
No runtime script or font writer is introduced by this retirement-only batch.
"""

import ast
import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from historical_sources import archived_source, recorded_sha256

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path(os.environ.get("FONTLAB_REFERENCE_ROOT", str(ROOT.parent)))
STUBS = WORKSPACE / "fontlab-echopy/src/fontlab_echopy/PythonQt"
DOCS = WORKSPACE / "fontlab-python-docs/docs/reference/PythonQt"
REASONS = {
    "blockingfortuneclient": "QtNetwork.QTcpSocket is exported; blocking/threaded fortune text has no current-font action or FontLab-consumable output.",
    "broadcastreceiver": "QtNetwork.QUdpSocket is exported; receiving demo datagrams has no glyph action or FontLab-consumable output.",
    "broadcastsender": "QtNetwork.QUdpSocket is exported; sending demo datagrams has no font payload or FontLab consumer.",
    "fortuneclient": "QtNetwork.QTcpSocket is exported; random fortune retrieval has no font action or FontLab-consumable output.",
    "fortuneserver": "QtNetwork.QTcpServer is exported; serving fortune strings has no font payload or FontLab consumer.",
    "http": "QtNetwork.QNetworkAccessManager is exported; this generic demo transfer has no font-specific input, validation or FontLab open/import action.",
    "lightmaps": "QtNetwork.QNetworkAccessManager is exported; geographic tile navigation has no glyph coordinates, font action or FontLab-consumable output.",
    "loopback": "QtNetwork.QTcpSocket and QTcpServer are exported; a 50 MiB transfer benchmark has no font action or FontLab-consumable output.",
    "threadedfortuneserver": "QtNetwork.QTcpServer is exported; worker-thread fortune service has no font payload or FontLab consumer.",
    "localfortuneclient": "QtNetwork.QLocalSocket is exported; local fortune retrieval has no font action or FontLab-consumable output.",
    "localfortuneserver": "QtNetwork.QLocalServer is exported; local fortune service has no font payload or FontLab consumer.",
    "sharedmemory": "QtCore.QSharedMemory has no exported detach method and its data/constData return Any; safe image-buffer transfer is not established, and the demo has no font action.",
    "dbus": "QtDBus is absent from the PythonQt export stubs; session-bus chat, ping and car demos have no FontLab font action.",
    "remoteobjects": "QtRemoteObjects is absent from the PythonQt export stubs; remote replicas and demo models have no FontLab font action.",
    "qml": "QtQml is absent from the PythonQt export stubs; declarative type/property lessons cannot run and have no FontLab font action.",
    "quick": "QtQuick and QtQml are absent from the PythonQt export stubs; scene/model lessons cannot run and have no FontLab font action.",
    "qtdemo": "QtQuick and QtQml are absent from the PythonQt export stubs; qtdemo also launches external PyQt/qmlscene/Assistant, contrary to the host's single-Qt-runtime rule; it is a demo launcher, not a font tool.",
    "multimedia": "QtMultimedia is absent from the PythonQt export stubs; audio device/output demos cannot run and have no FontLab font action.",
    "multimediawidgets": "QtMultimedia and QtMultimediaWidgets are absent from the PythonQt export stubs; camera/video demos cannot run and have no FontLab font action.",
    "webkit": "QtWebKit and QtWebKitWidgets are absent from the PythonQt export stubs; browser/DOM demos cannot run and provide no font-specific import or proof output.",
    "activeqt": "QAxContainer.QAxWidget is absent from the PythonQt export stubs; the Windows ActiveX browser is not a FontLab font workflow.",
    "painter-toy": "QtGui.QPlainTextEdit and QPainter are exported; this sample paints bullet holes over editor clicks, reports sound_supported=False, and has no font action or reusable font artwork output.",
    "launcher": "This is the obsolete example dispatch/lifetime mechanism, not a font tool; current Scripts entries launch directly through Fly and App.",
}
MISSING_MODULES = (
    "QtDBus",
    "QtRemoteObjects",
    "QtQml",
    "QtQuick",
    "QtMultimedia",
    "QtMultimediaWidgets",
    "QtWebKit",
    "QtWebKitWidgets",
    "QAxContainer",
)
GROUP_COUNTS = {
    "network": 18,
    "ipc": 5,
    "dbus": 6,
    "remoteobjects": 6,
    "qml": 10,
    "quick": 11,
    "qtdemo": 1,
    "multimedia": 3,
    "multimediawidgets": 4,
    "webkit": 6,
    "activeqt": 1,
    "launcher": 1,
}
IDENTITIES: tuple[tuple[str, str, str], ...] = (
    (
        "rescued/part1/launcher.py",
        "915eb0d92ab3d33020d4824b151cb0c6066fd323702f9e1073b70fbd6cb20f6e",
        "launcher",
    ),
    (
        "rescued/part2/ports/ipc/pyqt-official/localfortuneclient-0ad3432ccdca7ac0.py",
        "98083bf73c30f6dbf2fd96c1c38bcc19b391b72a9d237f462d5b65ddcdae0f1b",
        "localfortuneclient",
    ),
    (
        "rescued/part2/ports/ipc/pyqt-official/localfortuneserver-a14d08fe23965bec.py",
        "d322641e77e18333c3cd714ab4a4284e581f1a66bb4662e2dad9cb99fcc0f9e3",
        "localfortuneserver",
    ),
    (
        "rescued/part2/ports/multimedia/pyqt-examples/main-1151b1cb878f192a.py",
        "1b1bb01481bf852d248c294262da0aa4b9d951612f54d67e3dc911ec2ce5f4a5",
        "painter-toy",
    ),
    (
        "rescued/part2/ports/network/pyqt-official/blockingfortuneclient-79f3a23172968ad2.py",
        "af03d261d537f43fd4dc1d95afcd955d8541a5d93319682ab9ef1101ae57b008",
        "blockingfortuneclient",
    ),
    (
        "rescued/part2/ports/network/pyqt-official/broadcastreceiver-0bba8a80541ab04f.py",
        "42ca8d5473c19dd7a6f52fb6f5e40446bbbf6c35e9be4c1df580b2033929975f",
        "broadcastreceiver",
    ),
    (
        "rescued/part2/ports/network/pyqt-official/broadcastsender-90721289b8108c4f.py",
        "81fc0d312685559e33f55770c1c18712270650e596f2b95c0dc55621c5a83ca4",
        "broadcastsender",
    ),
    (
        "rescued/part2/ports/network/pyqt-official/fortuneclient-fbb4e3c7288fed7c.py",
        "44d8bdaa6054cc2fff97fea6105bff9676daa0ccbee09d40dd4d723e75445974",
        "fortuneclient",
    ),
    (
        "rescued/part2/ports/network/pyqt-official/fortuneserver-aad57160cfd51894.py",
        "c99314f9440fd178a7397108f7404747250e1290f0a05dccde962946d1db1eaa",
        "fortuneserver",
    ),
    (
        "rescued/part2/ports/network/pyqt-official/http-409f3d46a9555f23.py",
        "b17195fea6d4c5a79ae545b65c50cd517d1a4895330a0a1141cdb4b6f1026985",
        "http",
    ),
    (
        "rescued/part2/ports/network/pyqt-official/lightmaps-d8803c2afaabf3d5.py",
        "01f0daa234beef21a9d149bf661f21fcafe2d47095547c1d7fdd7afb04f8491b",
        "lightmaps",
    ),
    (
        "rescued/part2/ports/network/pyqt-official/loopback-ebf87d5f5390b0fd.py",
        "3bedd6701165136b3a1fc0d865adf890d1c64862b9bc0f8386fd64e21ec3f633",
        "loopback",
    ),
    (
        "rescued/part2/ports/network/pyqt-official/threadedfortuneserver-98f207907001ce47.py",
        "1a2d92f70bfc95d27b54284863ec07891b3bce6285c257777888317e2b537af1",
        "threadedfortuneserver",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/activeqt/pyqt-official/webbrowser-a1273c8940d43221.py",
        "794d3101898dd5799fbbf6d96eeebfe0bb5b7f38ede5b5e51702ab2daf501d3a",
        "activeqt",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/dbus/pyqt-official/car-54c7440bdcdc3dfc.py",
        "4e90d694226246707762fb4784007082305652169728d50a494c3d459dbffccd",
        "dbus",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/dbus/pyqt-official/chat-38465a8f4b1a229f.py",
        "1558e2d2bc4b55eeff0d0a13ad71708f0d590263f402985a972c4dac301945e4",
        "dbus",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/dbus/pyqt-official/controller-3cf5db95a691d200.py",
        "54924bf7f36c1d5f53a27934785703fdb9610a80d5f00d3a16173be7d5b59ee8",
        "dbus",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/dbus/pyqt-official/listnames-ab719a6a5c3afe4a.py",
        "dfc7a27833a60e8cef81109daf6b939a9638b0554115ccb3a2e2a39c4e667634",
        "dbus",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/dbus/pyqt-official/ping-30cfa75ad45b3447.py",
        "4417c3601bbc07e6a684eba9d833879de4d7fc8827410896cb529903c14ca2f1",
        "dbus",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/dbus/pyqt-official/pong-57a381bc8260c85d.py",
        "149d01b4e5bad67ffe3434a59d6697ee9282b7125fc069e6bd79952773db520d",
        "dbus",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/ipc/pyqt-official/localfortuneclient-0ad3432ccdca7ac0.py",
        "bd363989b8bb46cfbee4ea83a28d8a8fdb34a9e784edd9794b773d40a2db79ca",
        "localfortuneclient",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/ipc/pyqt-official/localfortuneserver-a14d08fe23965bec.py",
        "47abc6a76a26c6318bbd9db175b51a82422a69b7baad5b5904185e8b1536d93a",
        "localfortuneserver",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/ipc/pyqt-official/sharedmemory-de35a965dfcfd678.py",
        "a94737070771a8b73be8b767b0c90e9c0cdeabcce742d53a6eba580624e58e0b",
        "sharedmemory",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/multimedia/pyqt-official/audiodevices-74af8d8d2d7774b8.py",
        "b9e6800acf6b23f751e324271409a2c1fbbebb6762ebe27b40f34d9947c42a74",
        "multimedia",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/multimedia/pyqt-official/audiooutput-c391afd8516131e1.py",
        "424dd56877df3ea8c2ed47bd9379b23ce1ae8d8f2334afe20b8bf863d91f6671",
        "multimedia",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/multimediawidgets/pyqt-official/camera-f6d352360ae9bdfb.py",
        "301dc4123b766e7d68ba039dbda59a861df0d3c9676aea09c1eb079927868845",
        "multimediawidgets",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/multimediawidgets/pyqt-official/player-5eb4b9eaa2d5c9dc.py",
        "22b24e002b250c6d767b9705a7efaca3be0a3b1e85421f89586691863a09e276",
        "multimediawidgets",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/multimediawidgets/pyqt-official/videographicsitem-a57a89e523c75b7f.py",
        "f5e1d6806285591e47890cd6d44c3a67961132a94bce31d6deda5b6ead51f9c9",
        "multimediawidgets",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/multimediawidgets/pyqt-official/videowidget-481c128fba3a714b.py",
        "50227f840de3315323255bae675e83ac557e2ab5bb6938a47fe965c0869ec795",
        "multimediawidgets",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/network/pyqt-official/blockingfortuneclient-79f3a23172968ad2.py",
        "4067d4ed059520a71dbdbb7ffd80b6753182daeed7fee50fc51c43e844bc1085",
        "blockingfortuneclient",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/network/pyqt-official/broadcastreceiver-0bba8a80541ab04f.py",
        "e2bf246db1f1259527f94660f89d72fe631c7a5d24372e7aa9b7738f8d3cd4f7",
        "broadcastreceiver",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/network/pyqt-official/broadcastsender-90721289b8108c4f.py",
        "cfff739cb86415275d434df4f7a3d6bd2a59e3e5e267599feb63841c3fbae536",
        "broadcastsender",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/network/pyqt-official/fortuneclient-fbb4e3c7288fed7c.py",
        "7911898d499aa5b3efc71531c836bf7facd6c34678ff3b7e108da7ce91858508",
        "fortuneclient",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/network/pyqt-official/fortuneserver-aad57160cfd51894.py",
        "b84aa04982b034daa49347676d1e3cbe68d2fec8c22bc60ac5ba0de91dffd537",
        "fortuneserver",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/network/pyqt-official/http-409f3d46a9555f23.py",
        "f8599124fe34a81144709863e10bdeca76aa7c3872912c8daac44f89b626ba46",
        "http",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/network/pyqt-official/lightmaps-d8803c2afaabf3d5.py",
        "46319a969cdd2fdcdcde519e19a4b3ffa088c499e08840b5c9ad81063a3dcc1e",
        "lightmaps",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/network/pyqt-official/loopback-ebf87d5f5390b0fd.py",
        "ac195fe1f0e0e0fb1564a793bc80e248557451b173ab10fe3d1de943119c5f98",
        "loopback",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/network/pyqt-official/threadedfortuneserver-98f207907001ce47.py",
        "5366669ef1ec9f188248aee871b5bd9b58a492eab781d559342b98004b670b7e",
        "threadedfortuneserver",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/adding-8847cbce50b72500.py",
        "c066dac22e9f3718b16a497ca4bbcfbaa846963d0b1f0a0e9c8cb0d46f976054",
        "qml",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/attached-dd226ba9fbb7b330.py",
        "4d7ff622b8ddcc9d0050ae6a8d2d17809390adf6f46303e49bab62be08729a2c",
        "qml",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/binding-eb7a89f07f63cca7.py",
        "92d28200fb31c2bc433069973ec8b38098257ed3d89cd07e34a59be6b3670489",
        "qml",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/coercion-ad499afe23726248.py",
        "ac5da87b44ac518f746d9eb23d5086f70ba29c22d3e7aef33c760c577f89a596",
        "qml",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/default-6417cdcf1bfd1752.py",
        "ac5da87b44ac518f746d9eb23d5086f70ba29c22d3e7aef33c760c577f89a596",
        "qml",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/grouped-81a6f0d16c203608.py",
        "ac5da87b44ac518f746d9eb23d5086f70ba29c22d3e7aef33c760c577f89a596",
        "qml",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/methods-75ca5ac77ecefd6d.py",
        "ac5da87b44ac518f746d9eb23d5086f70ba29c22d3e7aef33c760c577f89a596",
        "qml",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/properties-d0a18273fa604bb6.py",
        "ac5da87b44ac518f746d9eb23d5086f70ba29c22d3e7aef33c760c577f89a596",
        "qml",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/signal-0a13f60f5f0561db.py",
        "4d7ff622b8ddcc9d0050ae6a8d2d17809390adf6f46303e49bab62be08729a2c",
        "qml",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/valuesource-738a22ef3062ed51.py",
        "92d28200fb31c2bc433069973ec8b38098257ed3d89cd07e34a59be6b3670489",
        "qml",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/qtdemo/pyqt-official/qtdemo-85a56a1f3c25ccca.py",
        "d5d4689ba9fb3647505034c9795e2980e74194385127c8a6049240e81c5aa707",
        "qtdemo",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/abstractitemmodel-e1316fee99c63555.py",
        "fb7dca9b8bf9d7807cf77bd16fada62a2a66128ea1a986c0ccc3f5257e91ee24",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/animation-835281a1ab864833.py",
        "fb7dca9b8bf9d7807cf77bd16fada62a2a66128ea1a986c0ccc3f5257e91ee24",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/canvas-36246fcbffecdeba.py",
        "fb7dca9b8bf9d7807cf77bd16fada62a2a66128ea1a986c0ccc3f5257e91ee24",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/chapter1-basics-6b1f4f5590a5518a.py",
        "3730a3b39a987532372ad68d0d2253157e3270f025e67fec47a5715825439fd4",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/chapter2-methods-8d1557cbfed9c7a0.py",
        "3730a3b39a987532372ad68d0d2253157e3270f025e67fec47a5715825439fd4",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/chapter3-bindings-3cd3713a5dc9f6dc.py",
        "3730a3b39a987532372ad68d0d2253157e3270f025e67fec47a5715825439fd4",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/chapter4-custompropertytypes-831ac8ea61da03f3.py",
        "cbd25f2cde6efab037479ec38e939fb5ab0da67b119bc65ffb922e6da9d1ebc9",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/chapter5-listproperties-b88e7eb0fcb53264.py",
        "4fb0fc950f85967722ff58566b4e9f42b64423bb4e80c7ac24c7196d1628614a",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/customgeometry-34538a4e2600b918.py",
        "bb4d545d6ec4dc29a45617e8b45292caa9f3b809e16d9f4940527010960486ea",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/objectlistmodel-68d664f95f48ce52.py",
        "fb7dca9b8bf9d7807cf77bd16fada62a2a66128ea1a986c0ccc3f5257e91ee24",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/stringlistmodel-b64d66dbce7274fe.py",
        "fb7dca9b8bf9d7807cf77bd16fada62a2a66128ea1a986c0ccc3f5257e91ee24",
        "quick",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/remoteobjects/pyqt-official/directconnectdynamicclient-54cbd9afababdf71.py",
        "93a5261cbd68adbbe9ba54e27fd2d5035861e1536ca18564f1750f7852d24650",
        "remoteobjects",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/remoteobjects/pyqt-official/directconnectdynamicserver-2f1e2f679775d89e.py",
        "b6f8ebd2cf13ee70407c0cdc18c9588af4ac9f84f77f6a98a932bf8bc8307e0b",
        "remoteobjects",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/remoteobjects/pyqt-official/modelviewclient-4dbe92cd1e720dce.py",
        "93a5261cbd68adbbe9ba54e27fd2d5035861e1536ca18564f1750f7852d24650",
        "remoteobjects",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/remoteobjects/pyqt-official/modelviewserver-781a3a959215eb81.py",
        "21b573f92776793422d2af4bcca441efc2aec48e3b94dc23f266e6bc9a9af6c2",
        "remoteobjects",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/remoteobjects/pyqt-official/registryconnecteddynamicclient-333f0272885ca1b7.py",
        "93a5261cbd68adbbe9ba54e27fd2d5035861e1536ca18564f1750f7852d24650",
        "remoteobjects",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/remoteobjects/pyqt-official/registryconnecteddynamicserver-b83377c9b48aec14.py",
        "21b573f92776793422d2af4bcca441efc2aec48e3b94dc23f266e6bc9a9af6c2",
        "remoteobjects",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/webkit/pyqt-official/domtraversal-8d5ea81a74e30222.py",
        "b7c787401ac12c06fc6e0d955b6bc9bcca00eae2a37ca94b9f0da914f056b10b",
        "webkit",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/webkit/pyqt-official/fancybrowser-f4000cf8ca288375.py",
        "b7c787401ac12c06fc6e0d955b6bc9bcca00eae2a37ca94b9f0da914f056b10b",
        "webkit",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/webkit/pyqt-official/formextractor-6ed36280660df7ea.py",
        "b7c787401ac12c06fc6e0d955b6bc9bcca00eae2a37ca94b9f0da914f056b10b",
        "webkit",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/webkit/pyqt-official/framecapture-ca47b83fbf3f31b9.py",
        "a4a39af83910c72237ee28c89d9fed89b37016103784de6a9f9a08bb7b7c16d4",
        "webkit",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/webkit/pyqt-official/previewer-47298251b3c83ecf.py",
        "b7c787401ac12c06fc6e0d955b6bc9bcca00eae2a37ca94b9f0da914f056b10b",
        "webkit",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/webkit/pyqt-official/simpleselector-ae16288fede27692.py",
        "b7c787401ac12c06fc6e0d955b6bc9bcca00eae2a37ca94b9f0da914f056b10b",
        "webkit",
    ),
)


def test_inventory_when_batch_selected_then_all_72_identities_are_pinned() -> None:
    """Detect omitted variants, accidental additions and duplicate identities."""
    rows = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    expected = {
        row["target"]: row["target_sha256"]
        for row in rows
        if set(Path(row["target"]).parts).intersection(GROUP_COUNTS)
        or row["target"] == "rescued/part1/launcher.py"
    }
    actual = {source: digest for source, digest, _ in IDENTITIES}
    assert len(IDENTITIES) == len(actual) == 72, "Pin every source variant once."
    assert actual == expected, "Batch identities must match the frozen index."
    counts = Counter(
        next((part for part in Path(source).parts if part in GROUP_COUNTS), "launcher")
        for source in actual
    )
    assert counts == GROUP_COUNTS, "Preserve the twelve group denominators."
    families = {
        (
            next((p for p in Path(source).parts if p in GROUP_COUNTS), "launcher"),
            Path(source).stem.rsplit("-", 1)[0],
        )
        for source in actual
    }
    assert len(families) == 61, "The four rows contain 61 distinct families."


def archived_retirement_fragment() -> dict[str, list[dict[str, Any]]]:
    """Return exact tracker rows and NOTICE text without writing shared files.

    Apache-2.0 describes the preserved first-party sample under the owner's
    grant. Keep upstream licence metadata separately; copy no upstream code.
    Resolve metadata from the catalogue, never infer it from a demo's title.
    """
    indexed = {
        row["target"]: row
        for row in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    }
    catalogued: dict[str, dict[str, Any]] = {}
    for base in ("rescued/part2", "rescued/part3/pyqt-official-ports"):
        rows = json.loads(archived_source(base + "/catalog/ports.json").read_text())[
            "ports"
        ]
        catalogued.update({f"{base}/{row['target_path']}": row for row in rows})
    records = []
    for source, digest, reason in IDENTITIES:
        row = {
            "source_menu": indexed[source]["menu"],
            "source": source,
            "source_sha256": digest,
            "disposition": "retired",
            "reason": REASONS[reason],
            "license": "Apache-2.0",
            "source_body_redistributed": False,
            "notice_line": f"Retired without redistribution: {source}; preserved FontLab sample, Apache-2.0; no code or assets included.",
        }
        if source in catalogued:
            metadata = catalogued[source]
            row["preserved_catalog_license"] = metadata["license"]["selected"]
            # Part2 has independent implementations. Part3 retains the same
            # upstream idea's original licence and author evidence.
            counterpart = source.replace(
                "rescued/part2/", "rescued/part3/pyqt-official-ports/", 1
            )
            upstream = catalogued.get(counterpart, metadata)
            row["upstream_license"] = upstream["license"]["selected"]
            row["upstream_author"] = upstream["license"].get(
                "attribution", "The author's own FontLab sample"
            )
            row["upstream_source"] = upstream["source"]
        else:
            row["upstream_license"] = "Apache-2.0"
            row["upstream_author"] = "The author's own FontLab sample"
        records.append(row)
    return {"adaptations": [], "retirements": records}


def retirement_fragment() -> dict[str, list[dict[str, Any]]]:
    """Use local dispositions; external upstream catalogue auditing is separate."""
    shared = json.loads((ROOT / "menu-adaptations.json").read_text())
    sources = {source for source, _, _ in IDENTITIES}
    return {"adaptations": [], "retirements": [
        row for row in shared["retirements"] if row["source"] in sources
    ]}


def test_external_catalogue_metadata_when_available_then_identity_and_credits_match() -> None:
    rows = archived_retirement_fragment()["retirements"]
    assert {row["source"] for row in rows} == {source for source, _, _ in IDENTITIES}
    for row in rows:
        assert row["upstream_author"] and row["upstream_license"], row["source"]


@pytest.mark.parametrize("source,digest,reason", IDENTITIES)
def test_retirement_records_keep_hash_and_specific_basis(source: str, digest: str, reason: str) -> None:
    assert recorded_sha256(source) == digest, source
    assert reason in REASONS, source
    row = next(r for r in retirement_fragment()["retirements"] if r["source"] == source)
    assert row["source_sha256"] == digest and row["reason"] == REASONS[reason], source


@pytest.mark.parametrize("source,digest,reason", IDENTITIES)
def test_retirement_when_preserved_source_read_then_hash_and_basis_match(
    source: str, digest: str, reason: str
) -> None:
    """Bind every decision to real bytes; inspect blocked bodies without execution."""
    payload = archived_source(source).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == digest, source
    tree = ast.parse(payload, filename=source, feature_version=(3, 11))
    assert reason in REASONS, f"Missing concrete decision for {source}"
    if reason in {
        "dbus",
        "remoteobjects",
        "qml",
        "quick",
        "qtdemo",
        "multimedia",
        "multimediawidgets",
        "webkit",
        "activeqt",
        "sharedmemory",
    }:
        raises = [node for node in ast.walk(tree) if isinstance(node, ast.Raise)]
        assert any(
            isinstance(node.exc, ast.Call)
            and isinstance(node.exc.func, ast.Name)
            and node.exc.func.id == "NotImplementedError"
            for node in raises
        ), f"Recheck the recorded capability refusal: {source}"
    if reason == "painter-toy":
        assert b'"sound_supported": False' in payload, "This is a painter toy."
        assert b"self.holes.append(event.pos())" in payload, (
            "Reassess changed behaviour."
        )


@pytest.mark.parametrize("module", MISSING_MODULES)
def test_capability_when_export_absent_then_stub_and_docs_agree(module: str) -> None:
    """Check native exports, not alternative bindings or the old generic Qt prose."""
    tree = ast.parse((STUBS / "__init__.pyi").read_text())
    exports = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)
    )
    assert module not in exports, f"Reassess {module}: native export changed."
    assert not (STUBS / f"{module}.pyi").exists(), module
    assert not (DOCS / f"{module}.html").exists(), module
    assert (DOCS / "QtNetwork.html").is_file(), "Require the real PythonQt docs tree."


def test_network_when_exported_then_retirement_does_not_claim_module_absent() -> None:
    """Network support is real; these retirements are usefulness decisions."""
    tree = ast.parse((STUBS / "QtNetwork.pyi").read_text())
    classes = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    for name in (
        "QTcpServer",
        "QTcpSocket",
        "QUdpSocket",
        "QNetworkAccessManager",
        "QLocalServer",
        "QLocalSocket",
    ):
        assert name in classes, name
        assert (DOCS / "QtNetwork" / f"{name}.html").is_file(), name
    for source, _, reason in IDENTITIES:
        if "/network/" in source or reason.startswith("localfortune"):
            assert "is exported" in REASONS[reason] or "are exported" in REASONS[reason]
            assert "no " in REASONS[reason], source


def test_shared_memory_when_stub_read_then_release_and_buffer_gap_is_specific() -> None:
    """Do not confuse supplemental Qt documentation with exported methods."""
    tree = ast.parse((STUBS / "QtCore.pyi").read_text())
    cls = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "QSharedMemory"
    )
    methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    assert "detach" not in methods, "Reassess explicit shared segment release."
    for name in ("data", "constData"):
        assert ast.unparse(methods[name].returns) == "Any", name


def test_painter_when_stub_read_then_widgets_are_available() -> None:
    """The numbered painter example is retired for purpose, not missing media."""
    tree = ast.parse((STUBS / "QtGui.pyi").read_text())
    names = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    assert {"QPlainTextEdit", "QPainter"} <= names, "Reassess the painter rationale."


def test_fragment_when_serialized_then_every_identity_has_provenance() -> None:
    """Check merge-ready rows; do not mutate the frozen rescue index or menus."""
    fragment = json.loads(json.dumps(retirement_fragment()))
    assert fragment["adaptations"] == [], "No replacement menu is proposed."
    records = fragment["retirements"]
    assert len(records) == 72, "Emit one exact object per identity."
    assert len({row["source_menu"] for row in records}) == 72, "Unique source menus."
    existing = json.loads((ROOT / "menu-adaptations.json").read_text())
    adapted = {row["source"] for row in existing["adaptations"]}
    for row in records:
        assert row["source"] not in adapted, "A delivered tool needs duplicate review."
        assert row["disposition"] == "retired", row["source"]
        assert row["license"] == "Apache-2.0", row["source"]
        assert row["source"] in (ROOT / "NOTICE").read_text(), row["source"]
        assert not (ROOT / row["source_menu"]).exists(), "Never restore the dispatcher."
