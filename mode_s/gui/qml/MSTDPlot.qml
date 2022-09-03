import QtCharts 2.15
import QtQml 2.15
import "qrc:/scripts/plot.js" as PLT

ChartView {
    id: chartView
    property bool std: True
    property var bar
    property var ivv
    property var windows: []
    
    property var diff
    property real threshold

    property string address: ""
    property string identification: ""

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
        id: series
        name: std ? "BAR" : "Diff" 
        color: std ? "blue" : "green"
        pointsVisible: false
        width: 4
    }

    LineSeries {
        id: secondSeries
        name: std ? "IVV" : "Threshold"
        color: "red"
        style: std ? 1 : 2 // Qt.SolidLine : Qt.DashLine
        pointsVisible: false
        width: 4
    }

    function update() {
        console.info("Displaying", title)
        if (std) {
            for (let index = 0; index < windows.length; index++) {
                PLT.appendVerticalLine(windows[index], bar[index], series)
                PLT.appendVerticalLine(windows[index], ivv[index], secondSeries)
            }

            let maxBar = Math.max.apply(null, bar)
            let maxIvv = Math.max.apply(null, ivv)
            let minBar = Math.min.apply(null, bar)
            let minIvv = Math.min.apply(null, ivv)
            yAxis.max = Math.max(maxBar, maxIvv)
            yAxis.min = Math.min(minBar, minIvv)

        } else {
            secondSeries.append(0, threshold)
            secondSeries.append(windows[windows.length -1], threshold)

            for (let index = 0; index < windows.length; index++) {
                PLT.appendVerticalLine(windows[index], diff[index], series)
            }

            yAxis.max = Math.max.apply(null, diff)
            yAxis.min = Math.min.apply(null, diff)
        }

        xAxis.max = Math.max.apply(null, windows)
        xAxis.min = Math.min.apply(null, windows)
        xAxis.applyNiceNumbers()
        yAxis.applyNiceNumbers()
    }

    onThresholdChanged: update()
}
