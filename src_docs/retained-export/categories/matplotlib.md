# Examples: matplotlib

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

31 records: 0 implemented, 31 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [QtExamples matplotlib/barchart_demo](#qtexamples-matplotlibbarchart_demo) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/date](#qtexamples-matplotlibdate) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/ellipse_demo](#qtexamples-matplotlibellipse_demo) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/fill](#qtexamples-matplotlibfill) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/histogram_features](#qtexamples-matplotlibhistogram_features) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/image_demo](#qtexamples-matplotlibimage_demo) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/legend](#qtexamples-matplotliblegend) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/log_demo](#qtexamples-matplotliblog_demo) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/main](#qtexamples-matplotlibmain) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/path_patch](#qtexamples-matplotlibpath_patch) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/pcolormesh_levels](#qtexamples-matplotlibpcolormesh_levels) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/pie_features](#qtexamples-matplotlibpie_features) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/plot_streamplot](#qtexamples-matplotlibplot_streamplot) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/polar_demo](#qtexamples-matplotlibpolar_demo) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/scatter_demo2](#qtexamples-matplotlibscatter_demo2) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/simple_plot](#qtexamples-matplotlibsimple_plot) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/subplot](#qtexamples-matplotlibsubplot) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/Subplot](#qtexamples-matplotlibsubplot_1) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/surface3d](#qtexamples-matplotlibsurface3d) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/table_demo](#qtexamples-matplotlibtable_demo) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/tex_demo](#qtexamples-matplotlibtex_demo) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/widgets/buttons](#qtexamples-matplotlibwidgetsbuttons) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/widgets/check_buttons](#qtexamples-matplotlibwidgetscheck_buttons) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/widgets/cursor](#qtexamples-matplotlibwidgetscursor) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/widgets/lasso_selector_demo](#qtexamples-matplotlibwidgetslasso_selector_demo) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/widgets/menu](#qtexamples-matplotlibwidgetsmenu) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/widgets/multicursor](#qtexamples-matplotlibwidgetsmulticursor) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/widgets/radio_buttons](#qtexamples-matplotlibwidgetsradio_buttons) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/widgets/rectangle_selector](#qtexamples-matplotlibwidgetsrectangle_selector) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/widgets/slider_demo](#qtexamples-matplotlibwidgetsslider_demo) | blocked | not run | GPL-3.0-only |
| [QtExamples matplotlib/widgets/span_selector](#qtexamples-matplotlibwidgetsspan_selector) | blocked | not run | GPL-3.0-only |

### QtExamples matplotlib/barchart_demo

- Source: [eyllanesc/QtExamples / others/matplotlib/barchart_demo.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/barchart_demo.py)
- Port: [`ports/matplotlib/eyllanesc/barchart-demo-52871219c50cdd21.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/barchart-demo-52871219c50cdd21.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/date

- Source: [eyllanesc/QtExamples / others/matplotlib/date.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/date.py)
- Port: [`ports/matplotlib/eyllanesc/date-7cc9bd76e925db18.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/date-7cc9bd76e925db18.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/ellipse_demo

- Source: [eyllanesc/QtExamples / others/matplotlib/ellipse_demo.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/ellipse_demo.py)
- Port: [`ports/matplotlib/eyllanesc/ellipse-demo-b76dc05cb743e9fc.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/ellipse-demo-b76dc05cb743e9fc.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/fill

- Source: [eyllanesc/QtExamples / others/matplotlib/fill.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/fill.py)
- Port: [`ports/matplotlib/eyllanesc/fill-43f4640a040ded3e.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/fill-43f4640a040ded3e.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/histogram_features

- Source: [eyllanesc/QtExamples / others/matplotlib/histogram_features.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/histogram_features.py)
- Port: [`ports/matplotlib/eyllanesc/histogram-features-26b75bfff47f567d.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/histogram-features-26b75bfff47f567d.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/image_demo

- Source: [eyllanesc/QtExamples / others/matplotlib/image_demo.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/image_demo.py)
- Port: [`ports/matplotlib/eyllanesc/image-demo-5354655012c2060e.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/image-demo-5354655012c2060e.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/legend

- Source: [eyllanesc/QtExamples / others/matplotlib/legend.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/legend.py)
- Port: [`ports/matplotlib/eyllanesc/legend-6cb023a08571bf96.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/legend-6cb023a08571bf96.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/log_demo

- Source: [eyllanesc/QtExamples / others/matplotlib/log_demo.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/log_demo.py)
- Port: [`ports/matplotlib/eyllanesc/log-demo-1ffcdfb872b0e689.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/log-demo-1ffcdfb872b0e689.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/main

- Source: [eyllanesc/QtExamples / others/matplotlib/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/main.py)
- Port: [`ports/matplotlib/eyllanesc/main-8fc6773f10b89095.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/main-8fc6773f10b89095.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas and NavigationToolbar2QT, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/path_patch

- Source: [eyllanesc/QtExamples / others/matplotlib/path_patch.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/path_patch.py)
- Port: [`ports/matplotlib/eyllanesc/path-patch-5c181bebc7c9773c.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/path-patch-5c181bebc7c9773c.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/pcolormesh_levels

- Source: [eyllanesc/QtExamples / others/matplotlib/pcolormesh_levels.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/pcolormesh_levels.py)
- Port: [`ports/matplotlib/eyllanesc/pcolormesh-levels-e2f27c6394aa70c8.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/pcolormesh-levels-e2f27c6394aa70c8.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/pie_features

- Source: [eyllanesc/QtExamples / others/matplotlib/pie_features.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/pie_features.py)
- Port: [`ports/matplotlib/eyllanesc/pie-features-5d8303b0b2237124.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/pie-features-5d8303b0b2237124.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/plot_streamplot

- Source: [eyllanesc/QtExamples / others/matplotlib/plot_streamplot.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/plot_streamplot.py)
- Port: [`ports/matplotlib/eyllanesc/plot-streamplot-19398065f86e2762.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/plot-streamplot-19398065f86e2762.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/polar_demo

- Source: [eyllanesc/QtExamples / others/matplotlib/polar_demo.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/polar_demo.py)
- Port: [`ports/matplotlib/eyllanesc/polar-demo-80aa961de86e1704.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/polar-demo-80aa961de86e1704.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/scatter_demo2

- Source: [eyllanesc/QtExamples / others/matplotlib/scatter_demo2.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/scatter_demo2.py)
- Port: [`ports/matplotlib/eyllanesc/scatter-demo2-2588c05ccd043d91.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/scatter-demo2-2588c05ccd043d91.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/simple_plot

- Source: [eyllanesc/QtExamples / others/matplotlib/simple_plot.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/simple_plot.py)
- Port: [`ports/matplotlib/eyllanesc/simple-plot-8cb9580232bd8081.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/simple-plot-8cb9580232bd8081.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/subplot

- Source: [eyllanesc/QtExamples / others/matplotlib/subplot.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/subplot.py)
- Port: [`ports/matplotlib/eyllanesc/subplot-207f7ce534696c20.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/subplot-207f7ce534696c20.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/Subplot

- Source: [eyllanesc/QtExamples / others/matplotlib/Subplot.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/Subplot.py)
- Port: [`ports/matplotlib/eyllanesc/subplot-f13380d705146bff.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/subplot-f13380d705146bff.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/surface3d

- Source: [eyllanesc/QtExamples / others/matplotlib/surface3d.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/surface3d.py)
- Port: [`ports/matplotlib/eyllanesc/surface3d-96777c686c66d526.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/surface3d-96777c686c66d526.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/table_demo

- Source: [eyllanesc/QtExamples / others/matplotlib/table_demo.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/table_demo.py)
- Port: [`ports/matplotlib/eyllanesc/table-demo-d82b14fd5e1eb010.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/table-demo-d82b14fd5e1eb010.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/tex_demo

- Source: [eyllanesc/QtExamples / others/matplotlib/tex_demo.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/tex_demo.py)
- Port: [`ports/matplotlib/eyllanesc/tex-demo-ee1562b25c092ee8.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/tex-demo-ee1562b25c092ee8.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/widgets/buttons

- Source: [eyllanesc/QtExamples / others/matplotlib/widgets/buttons.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/widgets/buttons.py)
- Port: [`ports/matplotlib/eyllanesc/buttons-60a3d030c4744735.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/buttons-60a3d030c4744735.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/widgets/check_buttons

- Source: [eyllanesc/QtExamples / others/matplotlib/widgets/check_buttons.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/widgets/check_buttons.py)
- Port: [`ports/matplotlib/eyllanesc/check-buttons-f5d13b3c5b699ab3.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/check-buttons-f5d13b3c5b699ab3.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/widgets/cursor

- Source: [eyllanesc/QtExamples / others/matplotlib/widgets/cursor.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/widgets/cursor.py)
- Port: [`ports/matplotlib/eyllanesc/cursor-620da7edd0cd23fc.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/cursor-620da7edd0cd23fc.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/widgets/lasso_selector_demo

- Source: [eyllanesc/QtExamples / others/matplotlib/widgets/lasso_selector_demo.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/widgets/lasso_selector_demo.py)
- Port: [`ports/matplotlib/eyllanesc/lasso-selector-demo-c6effccd6f31f416.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/lasso-selector-demo-c6effccd6f31f416.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/widgets/menu

- Source: [eyllanesc/QtExamples / others/matplotlib/widgets/menu.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/widgets/menu.py)
- Port: [`ports/matplotlib/eyllanesc/menu-f2767c945bece214.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/menu-f2767c945bece214.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/widgets/multicursor

- Source: [eyllanesc/QtExamples / others/matplotlib/widgets/multicursor.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/widgets/multicursor.py)
- Port: [`ports/matplotlib/eyllanesc/multicursor-21a081a01365c096.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/multicursor-21a081a01365c096.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/widgets/radio_buttons

- Source: [eyllanesc/QtExamples / others/matplotlib/widgets/radio_buttons.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/widgets/radio_buttons.py)
- Port: [`ports/matplotlib/eyllanesc/radio-buttons-22be270b0ff2abf7.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/radio-buttons-22be270b0ff2abf7.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/widgets/rectangle_selector

- Source: [eyllanesc/QtExamples / others/matplotlib/widgets/rectangle_selector.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/widgets/rectangle_selector.py)
- Port: [`ports/matplotlib/eyllanesc/rectangle-selector-01be5e33878e4940.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/rectangle-selector-01be5e33878e4940.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/widgets/slider_demo

- Source: [eyllanesc/QtExamples / others/matplotlib/widgets/slider_demo.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/widgets/slider_demo.py)
- Port: [`ports/matplotlib/eyllanesc/slider-demo-9007853b5b845ed9.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/slider-demo-9007853b5b845ed9.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.

### QtExamples matplotlib/widgets/span_selector

- Source: [eyllanesc/QtExamples / others/matplotlib/widgets/span_selector.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/others/matplotlib/widgets/span_selector.py)
- Port: [`ports/matplotlib/eyllanesc/span-selector-1862a5f7d89bd9b6.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/matplotlib/eyllanesc/span-selector-1862a5f7d89bd9b6.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed.
