# Examples: charts

2 records: 0 implemented, 2 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [QtExamples charts/barmodelmapper/main](#qtexamples-chartsbarmodelmappermain) | blocked | not run | GPL-3.0-only |
| [QtExamples charts/callout/main](#qtexamples-chartscalloutmain) | blocked | not run | GPL-3.0-only |

### QtExamples charts/barmodelmapper/main

- Source: [eyllanesc/QtExamples / official/charts/barmodelmapper/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/charts/barmodelmapper/main.py)
- Port: [`ports/charts/eyllanesc/main-c862c1b57a0a0412.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/charts/eyllanesc/main-c862c1b57a0a0412.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtCharts (QtChart); required native APIs: QBarCategoryAxis, QBarSeries, QChart, QChartView, QVBarModelMapper, QValueAxis. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.

### QtExamples charts/callout/main

- Source: [eyllanesc/QtExamples / official/charts/callout/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/charts/callout/main.py)
- Port: [`ports/charts/eyllanesc/main-6bd9cbb60a6ac008.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/charts/eyllanesc/main-6bd9cbb60a6ac008.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtCharts (QtChart); required native APIs: QChart, QLineSeries, QSplineSeries. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied.
