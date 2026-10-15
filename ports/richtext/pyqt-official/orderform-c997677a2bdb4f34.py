# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c997677a2bdb4f34.md
# this_file: ports/richtext/pyqt-official/orderform-c997677a2bdb4f34.py

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    item = getattr(obj, name)
    return item() if callable(item) else item


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


def workspace(handle):
    folder = TemporaryDirectory(prefix="fontlab-example-")
    handle.after_close.append(folder.cleanup)
    handle.controls["directory"] = folder.name
    return Path(folder.name)


import html

PRODUCTS = (("Drawing notebook", 1200), ("Graph pencil", 250), ("Paper ruler", 400))


def quantities(texts):
    values = []
    for text in texts:
        number = int(str(text).strip())
        if not 0 <= number <= 10000:
            raise ValueError("Quantities must be between 0 and 10000")
        values.append(number)
    return values


def letter(name, address, counts, offers):
    rows = "".join(
        f"<tr><td>{html.escape(product)}</td><td>{count}</td><td>{price * count / 100:.2f}</td></tr>"
        for (product, price), count in zip(PRODUCTS, counts)
    )
    total = sum(price * count for (_, price), count in zip(PRODUCTS, counts))
    return (
        f"<h2>Order request</h2><p>For {html.escape(name)}<br>{html.escape(address).replace(chr(10), '<br>')}</p>"
        f"<p>Please prepare the following supplies for our next project.</p><table border='1'>{rows}</table>"
        f"<p>Total: {total / 100:.2f}</p><p>Future offers: {'requested' if offers else 'not requested'}.</p><p>Thank you for helping us put ideas on paper.</p>"
    )


def build(qt):
    gui = qt.QtGui
    with owned(qt, "Order letters") as (handle, layout):
        tabs = gui.QTabWidget(handle.widget)
        layout.addWidget(tabs)
        state = {"letters": 0, "dirty": False, "closing": False}
        handle.cleanup.append(lambda: state.update(closing=True))
        status = gui.QLabel("", handle.widget)
        layout.addWidget(status)
        root = workspace(handle)
        printer = gui.QPrinter(gui.QPrinter.HighResolution)
        printer.setOutputFormat(gui.QPrinter.PdfFormat)
        printer.setOutputFileName(str(root / "order.pdf"))
        from fontlabapp.widgets import OwnedWidget

        class Details(gui.QDialog):
            def closeEvent(self, event):
                if state["closing"]:
                    event.accept()
                    return
                event.ignore()
                cancel()

        dialog = Details(handle.widget)
        handle.alerts.append(OwnedWidget(dialog, dialog))
        form = gui.QVBoxLayout(dialog)
        name = gui.QLineEdit(dialog)
        address = gui.QTextEdit(dialog)
        name.setText("Mira Rivers")
        address.setPlainText("12 Willow Walk\nHarbour")
        form.addWidget(gui.QLabel("Name", dialog))
        form.addWidget(name)
        form.addWidget(gui.QLabel("Address", dialog))
        form.addWidget(address)
        table = gui.QTableWidget(len(PRODUCTS), 3, dialog)
        table.setHorizontalHeaderLabels(["Item", "Unit price", "Quantity"])
        for row, (product, price) in enumerate(PRODUCTS):
            for col, text in enumerate((product, f"{price / 100:.2f}", "0")):
                item = gui.QTableWidgetItem(text)
                if col < 2:
                    item.setFlags(item.flags() & ~qt.QtCore.Qt.ItemIsEditable)
                table.setItem(row, col, item)
        form.addWidget(table)
        offers = gui.QCheckBox("Send future offers", dialog)
        feedback = gui.QLabel("", dialog)
        form.addWidget(offers)
        form.addWidget(feedback)

        def create():
            try:
                counts = quantities(
                    [table.item(row, 2).text() for row in range(len(PRODUCTS))]
                )
                customer = str(value(name, "text")).strip()
                if not customer or not any(counts):
                    raise ValueError("Enter a name and at least one positive quantity")
            except ValueError as error:
                feedback.setText(str(error))
                return
            editor = gui.QTextEdit(tabs)
            editor.setReadOnly(True)
            editor.setHtml(
                letter(
                    customer,
                    str(address.toPlainText()),
                    counts,
                    bool(value(offers, "checked")),
                )
            )
            state["letters"] += 1
            tabs.setCurrentIndex(tabs.addTab(editor, "Order " + str(state["letters"])))
            state["dirty"] = False
            dialog.hide()

        def discard():
            state["dirty"] = False
            dialog.hide()

        def cancel():
            if not state["dirty"]:
                dialog.hide()
                return
            box = gui.QMessageBox(dialog)
            box.setText("Discard these order details?")
            box.setStandardButtons(gui.QMessageBox.Discard | gui.QMessageBox.Cancel)
            handle.alerts.append(OwnedWidget(box, box))
            wire(
                handle,
                box,
                "finished(int)",
                lambda result: discard() if result == gui.QMessageBox.Discard else None,
            )
            box.open()

        for item, signal in (
            (name, "textChanged(QString)"),
            (address, "textChanged()"),
            (table, "cellChanged(int,int)"),
            (offers, "toggled(bool)"),
        ):
            wire(handle, item, signal, lambda *args: state.update(dirty=True))
        create_button = gui.QPushButton("Create letter", dialog)
        cancel_button = gui.QPushButton("Cancel", dialog)
        form.addWidget(create_button)
        form.addWidget(cancel_button)
        wire(handle, create_button, "clicked()", lambda *args: create())
        wire(handle, cancel_button, "clicked()", lambda *args: cancel())

        def print_active():
            editor = value(tabs, "currentWidget")
            if editor is None:
                status.setText("Create a letter before printing")
                return
            print_dialog = gui.QPrintDialog(printer, handle.widget)
            handle.alerts.append(OwnedWidget(print_dialog, print_dialog))

            def accepted(*args):
                output = str(value(printer, "outputFileName"))
                if output and not Path(output).resolve().is_relative_to(root.resolve()):
                    status.setText(
                        "Print output must stay inside the example directory"
                    )
                    return
                value(editor, "document").print(printer)

            wire(handle, print_dialog, "accepted()", accepted)
            print_dialog.open()

        button(qt, handle, layout, "New", dialog.open)
        button(qt, handle, layout, "Print", print_active)
        handle.controls.update(
            tabs=tabs,
            details=dialog,
            name=name,
            address=address,
            quantities=table,
            offers=offers,
            feedback=feedback,
            create=create,
            cancel=cancel,
            printer=printer,
        )
        handle.inspect_ui = lambda: {
            "letters": state["letters"],
            "dirty_details": state["dirty"],
        }
        return handle
