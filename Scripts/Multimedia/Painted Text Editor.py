# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/10 QPainter Python example/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
# this_file: Scripts/Multimedia/Painted Text Editor.py
"""Paint click marks over an editable document; save new UTF-8 files safely."""
from fontlab_python_lessons import qt_demos as S


def build(qt):
    with S.Session(qt, "Painted Text Editor") as s:
        s.vertical()
        holes = []

        class PaintedEditor(s.g.QPlainTextEdit):
            def mousePressEvent(self, event):
                point = event.pos()
                holes.append((int(point.x()), int(point.y())))
                s.g.QPlainTextEdit.mousePressEvent(self, event)
                self.viewport().update()

            def paintEvent(self, event):
                s.g.QPlainTextEdit.paintEvent(self, event)
                painter = s.g.QPainter(self.viewport())
                try:
                    painter.setBrush(s.g.QBrush(s.g.QColor("#885522")))
                    for x, y in holes:
                        painter.drawEllipse(s.c.QPointF(x, y), 5.0, 5.0)
                except Exception as error:
                    print("Painting failed:", error)
                finally:
                    painter.end()

        text = s.keep("text", PaintedEditor(s.window))
        s.keep("holes", holes)
        s.button("clear_marks", "Clear Click Marks", lambda: (holes.clear(), text.viewport().update()))
        s.add(text)
        status = s.label("Open a UTF-8 file or type text. Save creates a new file.")

        def open_file(path):
            if text.document().isModified():
                status.setText("Save your edited text before opening another file.")
                return
            try:
                content = S.Path(path).read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                status.setText(str(error))
                return
            text.setPlainText(content)
            text.document().setModified(False)
            status.setText(path)

        def save_file(path):
            try:
                with S.Path(path).open("x", encoding="utf-8") as stream:
                    stream.write(str(text.toPlainText()))
            except (OSError, UnicodeError) as error:
                status.setText(str(error))
                return
            text.document().setModified(False)
            status.setText("Saved " + path)

        def can_close():
            if not text.document().isModified():
                return True
            status.setText("Unsaved text: Save As, or use Discard Changes before Close.")
            return False

        def choose_file(callback, save=False):
            dialog = s.choose(callback, save=save)
            dialog.setDirectory(str(S.Path.home()))

        s.h.controls["can_close"] = can_close
        s.button("open", "Open", lambda: choose_file(open_file))
        s.button("save", "Save As", lambda: choose_file(save_file, save=True))
        s.button("discard", "Discard Changes", lambda: text.document().setModified(False))
        s.keep("open_file", open_file)
        s.keep("save_file", save_file)
        s.window.setWindowTitle("Text Editor")
        return s.h


def main():
    """Open this retained, parented PythonQt demo."""
    from fontlab_python_lessons.qt_demos import launch
    return launch(build, 'restored_painted_text_editor_1151b1cb878f192a', 'Painted Text Editor')


if __name__ == "__main__":
    main()

# ## MIT License
# 
# Upstream authorship attribution: Michael Herrmann. No copyright year or notice
# appears in the reviewed original files; none is inferred here.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
