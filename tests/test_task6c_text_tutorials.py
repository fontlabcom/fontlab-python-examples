# this_file: tests/test_task6c_text_tutorials.py
# SPDX-License-Identifier: Apache-2.0
"""Drive restored document and address workflows with offscreen Qt."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_restored_text_tutorials import ROOT, load, qt as base_qt


@pytest.fixture
def qt(base_qt, monkeypatch):
    qt_api, app = base_qt
    native_dialog = qt_api.QtGui.QFileDialog
    class FileDialog(native_dialog):
        AcceptOpen = native_dialog.AcceptMode.AcceptOpen
        AcceptSave = native_dialog.AcceptMode.AcceptSave
        def __init__(self, *args):
            super().__init__(*args)
            self.setOption(native_dialog.Option.DontUseNativeDialog, True)
    qt_api.QtGui.QFileDialog = FileDialog
    native_print_dialog = qt_api.QtGui.QPrintDialog
    class PrintDialog(native_print_dialog):
        def open(self):
            qt_api.QtGui.QDialog.open(self)
    qt_api.QtGui.QPrintDialog = PrintDialog
    monkeypatch.setattr(qt_api.QtGui.QTextDocument, 'print', qt_api.QtGui.QTextDocument.print_, raising=False)
    monkeypatch.setattr(qt_api.QtGui.QCheckBox, 'checked', property(qt_api.QtGui.QCheckBox.isChecked), raising=False)
    return qt_api, app


def launch_main(module, monkeypatch):
    from fontlab_python_lessons import qt_demos
    calls = []
    monkeypatch.setattr(qt_demos, 'launch', lambda build, *args: calls.append(build) or 'opened')
    assert module.main() == 'opened'
    assert calls == [module.build]


def exercise_session(module, session, qt, tmp_path):
    core, gui = qt.QtCore, qt.QtGui
    seen = []
    combo = session.combo('choice', ['a', 'b'], seen.append)
    combo.setCurrentIndex(1)
    assert seen == [1]
    button = session.button('probe', lambda: seen.append('button'))
    button.click()
    timer = session.timer('clock', lambda: seen.append('tick'), 1000)
    timer.timeout.emit()
    assert seen[-2:] == ['button', 'tick']
    menu = gui.QMenu(session.window)
    action = session.action(menu, 'probe action', lambda: seen.append('action'), True)
    action.trigger()
    assert seen[-1] == 'action'
    assert session.snapshot() == session.state
    root = session.root()
    assert session.path(root / 'safe.txt') == (root / 'safe.txt').resolve()
    for bad in [root, tmp_path.parent / 'outside.txt']:
        with pytest.raises(ValueError):
            session.path(bad)
    selected = []
    dialog = session.choose(False, selected.append)
    dialog.fileSelected.emit(str(root / 'input.txt'))
    assert selected == [str(root / 'input.txt')]
    def bad_file(path):
        raise ValueError('invalid selection')
    dialog = session.choose(True, bad_file)
    dialog.fileSelected.emit(str(root / 'bad.txt'))
    assert session.state['error'] == 'invalid selection'
    event = gui.QCloseEvent()
    session.state['dragging'] = True
    session.window.closeEvent(event)
    assert not event.isAccepted()
    with pytest.raises(RuntimeError, match='Finish the drag'):
        session.prepare_close()
    session.state['dragging'] = False
    saved = session.before_close
    session.before_close = lambda: seen.append('close requested')
    session.window.closeEvent(event)
    assert seen[-1] == 'close requested' and not event.isAccepted()
    session.before_close = saved
    session.closing = True
    session.window.closeEvent(event)
    assert event.isAccepted()
    session.closing = False
    assert module.value(SimpleNamespace(number=3), 'number') == 3


@pytest.mark.parametrize('stage', range(1, 8))
def test_address_collection_stages_keep_edits_search_and_files(stage, qt, monkeypatch, tmp_path):
    module = load(ROOT / f'Scripts/Tutorials/Address Collection Stage {stage}.py')
    monkeypatch.setattr(module, 'mkdtemp', lambda **kw: str(tmp_path))
    handle = module.build(qt[0])
    controls = handle.controls
    controller = controls['controller']
    if stage == 1:
        controls['name'].setText('Ada')
        controls['address'].setPlainText('First Street')
        assert handle.inspect_ui() == {'name': 'Ada', 'address': 'First Street'}
        exercise_session(module, controller, qt[0], tmp_path)
        handle.close()
    else:
        # Every stage retains the complete later-stage implementation; also test
        # it at its final capability level while preserving each declared build.
        assert controls['name'].isReadOnly()
        handle.close()
        monkeypatch.setattr(module, 'STAGE', 7)
        handle = module.build(qt[0])
        controls = handle.controls
        controller = controls['controller']
        controls['navigate'](1)
        controls['Add'].click()
        controls['submit']()
        assert 'Both fields' in controller.pending[-1].text()
        for name in ['Ada', 'Bea', 'Cai']:
            controls['name'].setText(name)
            controls['address'].setPlainText(name + ' street;\\\nTown')
            controls['submit']()
            assert controller.state['current'] == name
            if name != 'Cai':
                controls['Add'].click()
        controls['Add'].click()
        controls['name'].setText('Ada')
        controls['address'].setPlainText('Duplicate')
        controls['submit']()
        assert 'already belongs' in controller.pending[-1].text()
        controls['cancel']()
        controls['Edit'].click()
        controls['name'].setText('Cy')
        controls['submit']()
        assert 'Cy' in controls['contacts'] and 'Cai' not in controls['contacts']
        controls['navigate'](1)
        assert controller.state['current'] == 'Ada'
        controls['find']()
        controls['query'].clear()
        controls['find_result']()
        controls['query'].setText('unknown')
        controls['query'].returnPressed.emit()
        assert 'No contact' in controller.pending[-1].text()
        controls['find']()
        controls['query'].setText('Bea')
        controls['find_result']()
        assert controller.state['current'] == 'Bea'
        controls['remove'](False)
        assert 'Bea' in controls['contacts']
        controls['remove']()
        controller.pending[-1].finished.emit(qt[0].QtGui.QMessageBox.Yes)
        assert 'Bea' not in controls['contacts']
        output = tmp_path / 'contacts.json'
        controls['Save'].click()
        controller.pending[-1].fileSelected.emit(str(output))
        assert 'Ada' in output.read_text()
        controls['Load'].click()
        controller.pending[-1].fileSelected.emit(str(output))
        assert set(controls['contacts']) == {'Ada', 'Cy'}
        for bad in ['[]', '{}', '{"": "address"}', '{"Bad": 2}']:
            invalid = tmp_path / 'bad.json'
            invalid.write_text(bad)
            with pytest.raises(ValueError):
                controls['load_file'](invalid)
        controls['Export'].click()
        card = tmp_path / 'contact.vcf'
        controller.pending[-1].fileSelected.emit(str(card))
        assert b'BEGIN:VCARD\r\n' in card.read_bytes()
        exercise_session(module, controller, qt[0], tmp_path)
        handle.close()
        assert output.exists() and card.exists()
    launch_main(module, monkeypatch)
    monkeypatch.setattr(module, 'configure', lambda s: (_ for _ in ()).throw(ValueError('setup')))
    with pytest.raises(ValueError, match='setup'):
        module.build(qt[0])


@pytest.mark.parametrize('title', ['Text Application', 'Recent Text Files', 'Single Document Windows'])
def test_document_workspaces_save_guard_recent_and_window_actions(title, qt, monkeypatch, tmp_path):
    module = load(ROOT / f'Scripts/Main Windows/{title}.py')
    for mode in [module.MODE, 'application', 'recent', 'mdi', 'dock']:
        monkeypatch.setattr(module, 'MODE', mode)
        handle = module.build(qt[0])
        c = handle.controls
        s = c['controller']
        exercise_session(module, s, qt[0], tmp_path)
        doc = c['current']()
        editor = doc['editor']
        editor.insertPlainText('Saved draft')
        assert not c['can_close']()
        assert c['guard'](doc, lambda: 'done', 'cancel') is False
        assert c['guard'](doc, lambda: 'done', 'discard') == 'done'
        dialog = c['guard'](doc, lambda: None)
        dialog.finished.emit(qt[0].QtGui.QMessageBox.Cancel)
        assert doc['modified']
        assert c['save_document'](None) is False
        destination = tmp_path / (mode + '.txt')
        callback = []
        assert c['save_document'](doc, destination, lambda: callback.append(True))
        assert destination.read_text() == editor.toPlainText() and callback == [True]
        assert c['can_close']()
        assert not c['save_document'](doc, tmp_path / 'missing' / 'bad.txt')
        assert s.state['error']
        c['promote'](str(destination))
        assert s.state['recent'][0] == str(destination.resolve())
        c['open_file'](destination)
        assert not c['open_file'](tmp_path / 'missing.txt')
        if mode in ['application', 'dock']:
            c['new_document']('extra')
        else:
            extra = tmp_path / 'other.txt'
            extra.write_text('Other document')
            opened = c['open_file'](extra)
            assert opened['editor'].toPlainText() == 'Other document'
        for action in list(handle.widget.findChildren(qt[0].QtGui.QAction)):
            if action.text() in ['Copy', 'Cut', 'Paste', 'Undo', 'About', 'Tile', 'Cascade', 'Next', 'Previous']:
                action.trigger()
        if mode == 'mdi':
            windows = next(action.menu() for action in handle.widget.menuBar().actions() if action.text() == 'Window')
            windows.aboutToShow.emit()
            assert len(windows.actions()) >= 8
            windows.actions()[-1].trigger()
        if mode == 'dock':
            listing = c['Customers'].widget()
            listing.itemActivated.emit(listing.item(0))
            assert 'Rowan Vale' in editor.toPlainText()
        # Guarded New, Save As and Open use real asynchronous file choosers.
        for doc in c['documents']:
            doc['modified'] = False
        if mode in ['application', 'dock']:
            c['New1'].trigger()
            assert c['current']()['editor'].toPlainText() == ''
        unsaved = c['new_document']('new output')
        dialog = c['save_document'](unsaved)
        dialog.fileSelected.emit(str(tmp_path / (mode + '-new.txt')))
        assert Path(unsaved['path']).read_text() == 'new output'
        unsaved['editor'].insertPlainText('!')
        assert c['guard'](unsaved, lambda: 'saved', 'save')
        assert Path(unsaved['path']).read_text() == unsaved['editor'].toPlainText()
        for doc in c['documents']:
            doc['modified'] = False
        c['close_all']()
        assert handle.owner.closed
    launch_main(module, monkeypatch)


def actions(handle, qt):
    return {action.text(): action for action in handle.widget.findChildren(qt.QtGui.QAction)}


def test_rich_editor_formats_imports_images_and_exports(qt, monkeypatch, tmp_path):
    module = load(ROOT / 'Scripts/Rich Text/Rich Text Editor.py')
    monkeypatch.setattr(module, 'mkdtemp', lambda **kwargs: str(tmp_path))
    h = module.build(qt[0])
    c, gui = h.controls, qt[0].QtGui
    editor = c['editor']
    editor.selectAll()
    for label in ['Bold', 'Italic', 'Underline']:
        c[label].setChecked(True)
        c[label].setChecked(False)
    c['family'].setCurrentFont(gui.QFont('Helvetica'))
    c['size'].setCurrentText('18')
    qt[0].QtCore.QMetaObject.invokeMethod(c['size'], 'activated', qt[0].QtCore.Qt.DirectConnection, qt[0].QtCore.Q_ARG(str, '18'))
    assert editor.currentCharFormat().fontPointSize() == 18
    c['size'].setCurrentText('999')
    qt[0].QtCore.QMetaObject.invokeMethod(c['size'], 'activated', qt[0].QtCore.Qt.DirectConnection, qt[0].QtCore.Q_ARG(str, '999'))
    assert 'between 1 and 200' in c['status'].text()
    for index in range(9):
        c['styles'].setCurrentIndex(index)
    c['styles'].setCurrentIndex(0)
    aa = actions(h, qt[0])
    for label in ['Left', 'Center', 'Right', 'Justify', 'About']:
        aa[label].trigger()
    aa['Text color'].trigger()
    color_dialog = h.alerts[-1].widget
    color_dialog.setCurrentColor(gui.QColor('red'))
    color_dialog.accept()
    assert editor.currentCharFormat().foreground().color() == gui.QColor('red')
    imported = tmp_path / 'input'
    imported.mkdir()
    image = gui.QImage(4, 4, gui.QImage.Format_ARGB32)
    image.fill(gui.QColor('red'))
    image.save(str(imported / 'local.png'))
    html = imported / 'source.html'
    html.write_text('<p>Imported</p><img src="local.png"><img src="https://invalid/image.png"><img src="../outside.png">')
    c['open_file'](html)
    assert 'Imported' in editor.toPlainText()
    assert len(list((tmp_path / 'images').iterdir())) == 1
    source = imported / 'plain.txt'
    source.write_text('Plain source')
    c['open_file'](source)
    assert editor.toPlainText() == 'Plain source'
    c['open_file'](imported / 'missing')
    assert 'No such file' in c['status'].text()
    for bad in [tmp_path, tmp_path.parent / 'outside.txt', tmp_path / 'demonstration.html']:
        assert c['save_file'](bad) is False
    assert c['save_file'](tmp_path / 'no-directory' / 'a.txt') is False
    called = []
    assert c['save_file'](tmp_path / 'saved.txt', lambda: called.append(True))
    assert called == [True] and (tmp_path / 'saved.txt').read_text() == 'Plain source'
    assert c['save_file'](tmp_path / 'saved.html')
    c['export_pdf'](tmp_path / 'letter.pdf')
    assert (tmp_path / 'letter.pdf').read_bytes().startswith(b'%PDF')
    c['export_pdf'](tmp_path.parent / 'outside.pdf')
    assert 'Choose a new output' in c['status'].text()
    aa['Print'].trigger()
    qt[0].QtCore.QMetaObject.invokeMethod(h.alerts[-1].widget, 'accepted', qt[0].QtCore.Qt.DirectConnection)
    assert (tmp_path / 'printed.pdf').exists()
    aa['Preview'].trigger()
    h.alerts[-1].widget.paintRequested.emit(c['printer'])
    assert c['printer'].outputFileName().endswith('printed.pdf')
    c['guard'](lambda: called.append('clean'))
    assert called[-1] == 'clean'
    editor.insertPlainText('dirty')
    c['guard'](lambda: called.append('discard'))
    pending = h.alerts[-1].widget
    c['guard'](lambda: called.append('ignored'))
    pending.finished.emit(gui.QMessageBox.Discard)
    assert called[-1] == 'discard'
    c['guard'](lambda: called.append('save'))
    h.alerts[-1].widget.finished.emit(gui.QMessageBox.Save)
    assert called[-1] == 'save'
    aa['New'].trigger()
    assert editor.toPlainText() == ''
    editor.insertPlainText('new draft')
    c['guard'](lambda: called.append('new save'))
    h.alerts[-1].widget.finished.emit(gui.QMessageBox.Save)
    chooser = h.alerts[-1].widget
    chooser.selectFile(str(tmp_path / 'new.txt'))
    chooser.accepted.emit()
    assert (tmp_path / 'new.txt').read_text() == 'new draft'
    assert called[-1] == 'new save'
    aa['Open'].trigger()
    chooser = h.alerts[-1].widget
    chooser.selectFile(str(source))
    chooser.accepted.emit()
    assert editor.toPlainText() == 'Plain source'
    aa['Save As'].trigger()
    chooser = h.alerts[-1].widget
    chooser.selectFile(str(tmp_path / 'copy.txt'))
    chooser.accepted.emit()
    assert (tmp_path / 'copy.txt').exists()
    assert h.inspect_ui()['filename'].endswith('copy.txt')
    h.close()
    launch_main(module, monkeypatch)


def test_order_form_validates_details_discard_and_pdf(qt, monkeypatch, tmp_path):
    module = load(ROOT / 'Scripts/Rich Text/Order Letter Form.py')
    monkeypatch.setattr(module, 'mkdtemp', lambda **kwargs: str(tmp_path))
    h = module.build(qt[0])
    c, gui = h.controls, qt[0].QtGui
    c['Print'].click()
    assert c['tabs'].count() == 0
    c['New'].click()
    c['create']()
    assert 'positive quantity' in c['feedback'].text()
    c['quantities'].item(0, 2).setText('bad')
    c['create']()
    assert 'invalid literal' in c['feedback'].text()
    c['quantities'].item(0, 2).setText('2')
    c['offers'].setChecked(True)
    assert not c['can_close']()
    c['cancel']()
    h.alerts[-1].widget.finished.emit(gui.QMessageBox.Cancel)
    assert not c['can_close']()
    c['cancel']()
    h.alerts[-1].widget.finished.emit(gui.QMessageBox.Discard)
    assert c['can_close']()
    c['cancel']()
    c['create']()
    assert c['tabs'].count() == 1
    assert '24.00' in c['tabs'].currentWidget().toPlainText()
    assert 'requested' in c['tabs'].currentWidget().toPlainText()
    c['Print'].click()
    qt[0].QtCore.QMetaObject.invokeMethod(h.alerts[-1].widget, 'accepted', qt[0].QtCore.Qt.DirectConnection)
    assert (tmp_path / 'order.pdf').read_bytes().startswith(b'%PDF')
    c['printer'].setOutputFileName(str(tmp_path.parent / 'outside.pdf'))
    c['Print'].click()
    qt[0].QtCore.QMetaObject.invokeMethod(h.alerts[-1].widget, 'accepted', qt[0].QtCore.Qt.DirectConnection)
    assert h.inspect_ui()['letters'] == 1
    c['name'].setText('Changed')
    event = gui.QCloseEvent()
    c['details'].closeEvent(event)
    assert not event.isAccepted()
    h.alerts[-1].widget.finished.emit(gui.QMessageBox.Discard)
    h.close()
    launch_main(module, monkeypatch)


def test_source_highlighter_colors_multiline_and_opens_via_action(qt, monkeypatch, tmp_path):
    module = load(ROOT / 'Scripts/Rich Text/Source Syntax Highlighter.py')
    h = module.build(qt[0])
    c = h.controls
    sample = 'class Pond { int size() { return 4; } };\n/* blue\nwater */ "string"; // shore\nplain'
    c['editor'].setPlainText(sample)
    c['highlighter'].rehighlight()
    assert c['editor'].document().firstBlock().layout().formats()
    first_comment = c['editor'].document().findBlockByNumber(1)
    assert first_comment.userState() == 1
    assert first_comment.next().userState() == 0
    source = tmp_path / 'source.cpp'
    source.write_text('void function();')
    aa = actions(h, qt[0])
    aa['Open'].trigger()
    chooser = h.alerts[-1].widget
    chooser.selectFile(str(source))
    chooser.accepted.emit()
    assert c['editor'].toPlainText() == 'void function();'
    c['open_file'](tmp_path / 'missing')
    assert c['status'].text()
    aa['About'].trigger()
    assert 'comments may cross lines' in c['status'].text()
    aa['New'].trigger()
    assert c['editor'].toPlainText() == ''
    assert module.spans('"literal" // c')[0][0][2] == 'string'
    h.close()
    launch_main(module, monkeypatch)
