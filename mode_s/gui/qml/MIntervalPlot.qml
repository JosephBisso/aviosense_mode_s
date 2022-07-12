import QtCharts 2.15

ChartView {
    id: chartView
    property var points: []
    property var windows: []

    axes: [
        ValueAxis{
            id: xAxis
            min: 0
            max: 10000
            labelFormat:"%.0f ft/min"
        },
        ValueAxis{
            id: yAxis
            min: 0
            max: 10000
            labelFormat:"%.0f min"
        }
    ]

    LineSeries {
        id: slidingSeries
        name: "Slidings Windows"
        color: "blue"
        width: 4
    }

    onWindowsChanged: {
        for (let index = 0; index < windows.length; index++) {
            if (index > 0) {
                slidingSeries.append(windows[index], points[index-1])
            }
            slidingSeries.append(windows[index], points[index])
        }
        xAxis.max = Math.max.apply(null, windows)
        yAxis.max = Math.max.apply(null, points)
        xAxis.applyNiceNumbers()
        yAxis.applyNiceNumbers()
    }
}
