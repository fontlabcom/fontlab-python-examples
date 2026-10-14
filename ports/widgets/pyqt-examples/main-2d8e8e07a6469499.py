# this_file: ports/widgets/pyqt-examples/main-2d8e8e07a6469499.py
# SPDX-License-Identifier: BSD-3-Clause
# Adapted from Riverbank Computing Limited (2013); Nokia Corporation and/or subsidiaries (2010); Michael Herrmann, pyqt/examples: src/02 PyQt Widgets/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from typing import Any

from fontlab_python_examples.editor import apply_style
from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    QCheckBox = qt.QtGui.QCheckBox
    QComboBox = qt.QtGui.QComboBox
    QDateTime = qt.QtCore.QDateTime
    QDateTimeEdit = qt.QtGui.QDateTimeEdit
    QDial = qt.QtGui.QDial
    QDialog = qt.QtGui.QDialog
    QGridLayout = qt.QtGui.QGridLayout
    QGroupBox = qt.QtGui.QGroupBox
    QHBoxLayout = qt.QtGui.QHBoxLayout
    QLabel = qt.QtGui.QLabel
    QLineEdit = qt.QtGui.QLineEdit
    QProgressBar = qt.QtGui.QProgressBar
    QPushButton = qt.QtGui.QPushButton
    QRadioButton = qt.QtGui.QRadioButton
    QScrollBar = qt.QtGui.QScrollBar
    QSizePolicy = qt.QtGui.QSizePolicy
    QSlider = qt.QtGui.QSlider
    QSpinBox = qt.QtGui.QSpinBox
    QStyleFactory = qt.QtGui.QStyleFactory
    QTabWidget = qt.QtGui.QTabWidget
    QTableWidget = qt.QtGui.QTableWidget
    QTextEdit = qt.QtGui.QTextEdit
    QTimer = qt.QtCore.QTimer
    QVBoxLayout = qt.QtGui.QVBoxLayout
    QWidget = qt.QtGui.QWidget
    Qt = qt.QtCore.Qt

    handle = None

    class WidgetGallery(QDialog):
        def __init__(self, parent=None):
            nonlocal handle
            super().__init__(parent)
            handle = ExampleHandle(self, dict)
            self.controls = {}

            self.originalPalette = self.palette

            styleComboBox = QComboBox()
            styleComboBox.addItems(QStyleFactory.keys())

            styleLabel = QLabel("&Style:")
            styleLabel.setBuddy(styleComboBox)

            self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
            self.useStylePaletteCheckBox.setChecked(True)

            disableWidgetsCheckBox = QCheckBox("&Disable widgets")

            self.createTopLeftGroupBox()
            self.createTopRightGroupBox()
            self.createBottomLeftTabWidget()
            self.createBottomRightGroupBox()
            self.createProgressBar()

            handle.connect_old(styleComboBox, "activated(QString)", self.changeStyle)
            handle.connect(self.useStylePaletteCheckBox.toggled, self.changePalette)
            handle.connect(
                disableWidgetsCheckBox.toggled, self.topLeftGroupBox.setDisabled
            )
            handle.connect(
                disableWidgetsCheckBox.toggled, self.topRightGroupBox.setDisabled
            )
            handle.connect(
                disableWidgetsCheckBox.toggled, self.bottomLeftTabWidget.setDisabled
            )
            handle.connect(
                disableWidgetsCheckBox.toggled, self.bottomRightGroupBox.setDisabled
            )

            topLayout = QHBoxLayout()
            topLayout.addWidget(styleLabel)
            topLayout.addWidget(styleComboBox)
            topLayout.addStretch(1)
            topLayout.addWidget(self.useStylePaletteCheckBox)
            topLayout.addWidget(disableWidgetsCheckBox)

            mainLayout = QGridLayout()
            mainLayout.addLayout(topLayout, 0, 0, 1, 2)
            mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
            mainLayout.addWidget(self.topRightGroupBox, 1, 1)
            mainLayout.addWidget(self.bottomLeftTabWidget, 2, 0)
            mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)
            mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
            mainLayout.setRowStretch(1, 1)
            mainLayout.setRowStretch(2, 1)
            mainLayout.setColumnStretch(0, 1)
            mainLayout.setColumnStretch(1, 1)
            self.setLayout(mainLayout)

            self.setWindowTitle("Styles")
            self._style = self.style()
            self.changeStyle("Windows")

        def changeStyle(self, styleName):
            style = QStyleFactory.create(styleName)
            if style is not None:
                style.setParent(self)
                apply_style(self, style)
                self._style = style
            self.changePalette()

        def changePalette(self):
            if self.useStylePaletteCheckBox.isChecked():
                self.setPalette(self._style.standardPalette())
            else:
                self.setPalette(self.originalPalette)

        def advanceProgressBar(self):
            curVal = self.progressBar.value
            maxVal = self.progressBar.maximum
            self.progressBar.setValue(curVal + (maxVal - curVal) // 100)

        def createTopLeftGroupBox(self):
            self.topLeftGroupBox = QGroupBox("Group 1")

            radioButton1 = QRadioButton("Radio button 1")
            radioButton2 = QRadioButton("Radio button 2")
            radioButton3 = QRadioButton("Radio button 3")
            radioButton1.setChecked(True)

            checkBox = QCheckBox("Tri-state check box")
            checkBox.setTristate(True)
            checkBox.setCheckState(Qt.PartiallyChecked)
            self.controls.update(radio=radioButton1, tri_state=checkBox)

            layout = QVBoxLayout()
            layout.addWidget(radioButton1)
            layout.addWidget(radioButton2)
            layout.addWidget(radioButton3)
            layout.addWidget(checkBox)
            layout.addStretch(1)
            self.topLeftGroupBox.setLayout(layout)

        def createTopRightGroupBox(self):
            self.topRightGroupBox = QGroupBox("Group 2")

            defaultPushButton = QPushButton("Default Push Button")
            defaultPushButton.setDefault(True)

            togglePushButton = QPushButton("Toggle Push Button")
            togglePushButton.setCheckable(True)
            togglePushButton.setChecked(True)

            flatPushButton = QPushButton("Flat Push Button")
            flatPushButton.setFlat(True)

            layout = QVBoxLayout()
            layout.addWidget(defaultPushButton)
            layout.addWidget(togglePushButton)
            layout.addWidget(flatPushButton)
            layout.addStretch(1)
            self.topRightGroupBox.setLayout(layout)

        def createBottomLeftTabWidget(self):
            self.bottomLeftTabWidget = QTabWidget()
            self.bottomLeftTabWidget.setSizePolicy(
                QSizePolicy.Preferred, QSizePolicy.Ignored
            )

            tab1 = QWidget()
            tableWidget = QTableWidget(10, 10)

            tab1hbox = QHBoxLayout()
            tab1hbox.setContentsMargins(5, 5, 5, 5)
            tab1hbox.addWidget(tableWidget)
            tab1.setLayout(tab1hbox)

            tab2 = QWidget()
            textEdit = QTextEdit()

            textEdit.setPlainText(
                "Twinkle, twinkle, little star,\n"
                "How I wonder what you are.\n"
                "Up above the world so high,\n"
                "Like a diamond in the sky.\n"
                "Twinkle, twinkle, little star,\n"
                "How I wonder what you are!\n"
            )

            tab2hbox = QHBoxLayout()
            tab2hbox.setContentsMargins(5, 5, 5, 5)
            tab2hbox.addWidget(textEdit)
            tab2.setLayout(tab2hbox)

            self.controls.update(table=tableWidget, poem=textEdit)
            self.bottomLeftTabWidget.addTab(tab1, "&Table")
            self.bottomLeftTabWidget.addTab(tab2, "Text &Edit")

        def createBottomRightGroupBox(self):
            self.bottomRightGroupBox = QGroupBox("Group 3")
            self.bottomRightGroupBox.setCheckable(True)
            self.bottomRightGroupBox.setChecked(True)

            lineEdit = QLineEdit("s3cRe7")
            lineEdit.setEchoMode(QLineEdit.Password)

            spinBox = QSpinBox(self.bottomRightGroupBox)
            spinBox.setValue(50)

            dateTimeEdit = QDateTimeEdit(self.bottomRightGroupBox)
            dateTimeEdit.setDateTime(QDateTime.currentDateTime())

            slider = QSlider(Qt.Horizontal, self.bottomRightGroupBox)
            slider.setValue(40)

            scrollBar = QScrollBar(Qt.Horizontal, self.bottomRightGroupBox)
            scrollBar.setValue(60)

            dial = QDial(self.bottomRightGroupBox)
            dial.setValue(30)
            dial.setNotchesVisible(True)
            self.controls.update(
                password=lineEdit,
                spin=spinBox,
                slider=slider,
                scroll=scrollBar,
                dial=dial,
            )

            layout = QGridLayout()
            layout.addWidget(lineEdit, 0, 0, 1, 2)
            layout.addWidget(spinBox, 1, 0, 1, 2)
            layout.addWidget(dateTimeEdit, 2, 0, 1, 2)
            layout.addWidget(slider, 3, 0)
            layout.addWidget(scrollBar, 4, 0)
            layout.addWidget(dial, 3, 1, 2, 1)
            layout.setRowStretch(5, 1)
            self.bottomRightGroupBox.setLayout(layout)

        def createProgressBar(self):
            self.progressBar = QProgressBar()
            self.progressBar.setRange(0, 10000)
            self.progressBar.setValue(0)

            self.timer = QTimer(self)
            handle.connect(self.timer.timeout, self.advanceProgressBar)
            self.timer.start(1000)

    window = WidgetGallery()
    handle.inspect_ui = lambda: {
        "title": str(window.windowTitle),
        "progress": int(window.progressBar.value),
        "maximum": int(window.progressBar.maximum),
        "groups": [
            str(window.topLeftGroupBox.title),
            str(window.topRightGroupBox.title),
            str(window.bottomRightGroupBox.title),
        ],
        "tab_count": int(window.bottomLeftTabWidget.count),
        "poem": str(window.controls["poem"].toPlainText()),
        "table_rows": int(window.controls["table"].rowCount),
        "table_columns": int(window.controls["table"].columnCount),
        "password": str(window.controls["password"].text),
        "values": {
            name: int(window.controls[name].value)
            for name in ("spin", "slider", "scroll", "dial")
        },
        "radio_checked": bool(window.controls["radio"].isChecked()),
        "tri_state": int(window.controls["tri_state"].checkState()),
    }
    handle.callbacks.append(window.advanceProgressBar)
    handle.cleanup.append(lambda: None if handle.owner.closed else window.timer.stop())

    def release_widgets() -> None:
        nonlocal window
        if not handle.owner.closed:
            window.controls.clear()
            for name in (
                "useStylePaletteCheckBox",
                "topLeftGroupBox",
                "topRightGroupBox",
                "bottomLeftTabWidget",
                "bottomRightGroupBox",
                "progressBar",
                "timer",
                "_style",
            ):
                delattr(window, name)
        window = None

    handle.release.append(release_widgets)
    return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("2d8e8e07a6469499")
