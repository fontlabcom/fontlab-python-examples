# this_file: Scripts/Widgets/Dark Theme Editor.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/09 Qt dark theme/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.

"""Edit UTF-8 text and save new files; refuse Close while edits are unsaved."""

from fontlab_python_lessons import qt_demos as S


def build(qt):
    with S.Session(qt, "Text Editor") as s:
        s.vertical()
        text = s.keep("text", s.g.QPlainTextEdit(s.window))
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
        palette = s.g.QPalette()
        for role, color in ((s.g.QPalette.Window, "#353535"), (s.g.QPalette.Base, "#191919"), (s.g.QPalette.Text, "#eeeeee"), (s.g.QPalette.WindowText, "#eeeeee"), (s.g.QPalette.Button, "#353535"), (s.g.QPalette.ButtonText, "#eeeeee"), (s.g.QPalette.Highlight, "#2a82da")):
            palette.setColor(role, s.g.QColor(color))
        s.window.setPalette(palette)
        text.setPalette(palette)
        s.local_style("Fusion")
        return s.h


def main():
    """Open this retained, parented PythonQt demo."""
    from fontlab_python_lessons.qt_demos import launch
    return launch(build, 'restored_dark_theme_editor', 'Dark Theme Editor')


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
