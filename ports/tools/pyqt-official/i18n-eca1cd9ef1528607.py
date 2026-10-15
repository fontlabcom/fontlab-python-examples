# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/eca1cd9ef1528607.md
# this_file: ports/tools/pyqt-official/i18n-eca1cd9ef1528607.py

from contextlib import contextmanager

from fontlab_python_examples.handle import ExampleHandle


@contextmanager
def owned(qt, title):
    state = {"closing": False}

    class Window(qt.QtGui.QWidget):
        def closeEvent(self, event):
            if not state["closing"]:
                handle.close()
            event.accept()

    window = Window()
    handle = ExampleHandle(window, dict)
    handle.cleanup.append(lambda: state.update(closing=True))
    try:
        window.setWindowTitle(title)
        window.setAttribute(qt.QtCore.Qt.WA_QuitOnClose, False)
        window.resize(760, 540)
        layout = qt.QtGui.QVBoxLayout(window)
        handle.controls["layout"] = layout
        yield handle, layout
    except BaseException:
        handle.close()
        raise


def wire(handle, obj, signature, callback):
    def receive(*args):
        if not handle.owner.closed:
            callback(*args)

    handle.connect_old(obj, signature, receive)
    return receive


def button(qt, handle, layout, name, callback):
    item = qt.QtGui.QPushButton(name, handle.widget)
    layout.addWidget(item)
    handle.controls[name] = item
    wire(handle, item, "clicked()", lambda *args: callback())
    return item


CATALOGUES = {
    "English": (
        "#e8f1ff",
        ("Sample", "File", "Close", "Name", "Details", "List", "Grid", "Preview"),
    ),
    "Français": (
        "#f4e8ff",
        ("Exemple", "Fichier", "Fermer", "Nom", "Détails", "Liste", "Grille", "Aperçu"),
    ),
    "Deutsch": (
        "#fff1d6",
        (
            "Beispiel",
            "Datei",
            "Schließen",
            "Name",
            "Details",
            "Liste",
            "Raster",
            "Vorschau",
        ),
    ),
    "Español": (
        "#e3f5eb",
        (
            "Ejemplo",
            "Archivo",
            "Cerrar",
            "Nombre",
            "Detalles",
            "Lista",
            "Cuadrícula",
            "Vista previa",
        ),
    ),
    "Polski": (
        "#ffe5e7",
        (
            "Przykład",
            "Plik",
            "Zamknij",
            "Nazwa",
            "Szczegóły",
            "Lista",
            "Siatka",
            "Podgląd",
        ),
    ),
    "日本語": (
        "#e1f5f5",
        ("見本", "ファイル", "閉じる", "名前", "詳細", "一覧", "格子", "プレビュー"),
    ),
}
KEYS = ("Sample", "File", "Close", "Name", "Details", "List", "Grid", "Preview")


def build(qt):
    core, gui = qt.QtCore, qt.QtGui
    with owned(qt, "Language windows") as (handle, layout):
        checks, windows, translators = {}, {}, []
        closing = {"value": False}
        handle.cleanup.append(lambda: closing.update(value=True))

        def make_child(language, check):
            color, words = CATALOGUES[language]
            catalogue = dict(zip(KEYS, words))

            class Translator(core.QTranslator):
                def translate(self, context, sourceText, disambiguation=None, n=-1):
                    return catalogue.get(str(sourceText), str(sourceText))

            translator = Translator(handle.widget)
            translators.append(translator)

            def tr(key):
                return translator.translate("Sample", key)

            class Child(gui.QWidget):
                def closeEvent(self, event):
                    if closing["value"]:
                        event.accept()
                        return
                    check.setChecked(False)
                    self.hide()
                    event.ignore()

            child = Child(handle.widget, core.Qt.Window)
            child.setWindowTitle(tr("Sample") + " — " + language)
            child.setStyleSheet("background-color: " + color)
            box = gui.QVBoxLayout(child)
            box.addWidget(gui.QLabel(tr("Name"), child))
            box.addWidget(gui.QLineEdit(child))
            box.addWidget(gui.QLabel(tr("Details"), child))
            languages = gui.QListWidget(child)
            languages.addItems(list(CATALOGUES))
            box.addWidget(languages)
            for key in ("List", "Grid", "Preview"):
                box.addWidget(gui.QRadioButton(tr(key), child))
            bar = gui.QMenuBar(child)
            action = gui.QAction(tr("Close"), child)
            bar.addMenu(tr("File")).addAction(action)
            box.addWidget(bar)
            wire(handle, action, "triggered()", lambda *args: check.setChecked(False))
            from fontlabapp.widgets import OwnedWidget

            handle.alerts.append(OwnedWidget(child, child))
            return child

        for language in CATALOGUES:
            check = gui.QCheckBox(language, handle.widget)
            layout.addWidget(check)
            checks[language] = check
            child = make_child(language, check)
            windows[language] = child
            wire(
                handle,
                check,
                "toggled(bool)",
                lambda checked, window=child: window.setVisible(bool(checked)),
            )
        button(
            qt,
            handle,
            layout,
            "Show All",
            lambda: [c.setChecked(True) for c in checks.values()],
        )
        button(
            qt,
            handle,
            layout,
            "Hide All",
            lambda: [c.setChecked(False) for c in checks.values()],
        )
        handle.controls.update(checks=checks, windows=windows, translators=translators)
        handle.inspect_ui = lambda: {
            "languages": {
                name: bool(window.isVisible()) for name, window in windows.items()
            }
        }
        return handle
