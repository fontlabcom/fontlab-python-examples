# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/356e4e807f1e789f.md
# this_file: Scripts/Widgets/Calculator.py

"""Show calculator using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S

import math


class Arithmetic:
    def __init__(self):
        self.clear()
        self.memory = 0.0

    def clear(self):
        self.text = "0"
        self.terms = []
        self.fresh = True
        self.repeat = None

    def number(self, text):
        if self.fresh or self.text == "Error":
            self.text = "0"
            self.fresh = False
        if text == ".":
            if "." not in self.text:
                self.text += "."
        elif self.text == "0":
            self.text = text
        else:
            self.text += text

    def evaluate(self, tokens):
        work = [float(tokens[0])]
        ops = []
        for i in range(1, len(tokens), 2):
            op, b = tokens[i], float(tokens[i + 1])
            if op == "*":
                work[-1] *= b
            elif op == "/":
                work[-1] /= b
            else:
                ops.append(op)
                work.append(b)
        result = work[0]
        for op, b in zip(ops, work[1:]):
            result = result + b if op == "+" else result - b
        return result

    def command(self, key):
        try:
            if key.isdigit() or key == ".":
                self.number(key)
                return self.text
            if key == "C":
                self.clear()
                return self.text
            if key == "CE":
                self.text = "0"
                self.fresh = True
                return self.text
            if key == "Back":
                self.text = self.text[:-1] or "0"
                return self.text
            n = float(self.text)
            if key in "+-*/":
                if self.fresh and self.terms:
                    self.terms[-1] = key
                else:
                    self.terms.extend([n, key])
                self.fresh = True
            elif key == "=":
                if self.terms:
                    tokens = self.terms + [n]
                    self.repeat = (tokens[-2], tokens[-1])
                    n = self.evaluate(tokens)
                elif self.repeat:
                    n = self.evaluate([n, *self.repeat])
                self.text = format(0.0 if n == 0 else n, ".12g")
                self.terms = []
                self.fresh = True
            elif key in ["±", "sqrt", "square", "1/x"]:
                n = {
                    "±": lambda: -n,
                    "sqrt": lambda: math.sqrt(n),
                    "square": lambda: n * n,
                    "1/x": lambda: 1 / n,
                }[key]()
                self.text = format(0.0 if n == 0 else n, ".12g")
                self.fresh = True
            elif key == "MC":
                self.memory = 0.0
            elif key == "MR":
                self.text = format(self.memory, ".12g")
                self.fresh = True
            elif key == "MS":
                self.memory = n
                self.fresh = True
            elif key == "M+":
                self.memory += n
                self.fresh = True
        except (ValueError, ZeroDivisionError, OverflowError):
            self.text = "Error"
            self.terms = []
            self.fresh = True
            self.repeat = None
        return self.text


def build(qt):
    with S.Session(qt, "Calculator") as s:
        s.vertical()
        engine = Arithmetic()
        display = s.line("display", "0")
        display.setReadOnly(True)
        display.setAlignment(s.c.Qt.AlignRight)
        grid = s.g.QGridLayout()
        s.layout.addLayout(grid)
        keys = [
            "MC",
            "MR",
            "MS",
            "M+",
            "C",
            "CE",
            "Back",
            "±",
            "7",
            "8",
            "9",
            "/",
            "4",
            "5",
            "6",
            "*",
            "1",
            "2",
            "3",
            "-",
            "0",
            ".",
            "=",
            "+",
            "sqrt",
            "square",
            "1/x",
        ]

        def press(key):
            display.setText(engine.command(key))
            s.state.update(display=engine.text, memory=engine.memory)

        for i, key in enumerate(keys):
            button = s.keep(key, s.g.QPushButton(key, s.window))
            grid.addWidget(button, i // 4, i % 4)
            s.link(button, "clicked()", lambda *a, k=key: press(k))
        s.keep("press", press)
        return s.h


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_calculator-356e4e807f1e789f', 'Calculator')


if __name__ == "__main__":
    main()
