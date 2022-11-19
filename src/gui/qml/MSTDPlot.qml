import QtQml 2.15
import QtCharts 2.15
import "qrc:/scripts/util.js" as Util

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
    animationOptions: ChartView.SeriesAnimations

    MZoomableArea {
        control: chartView
    }

    LineSeries {
        id: series
        name: std ? "BAR" : "Diff" 
        color: std ? "blue" : "green"
        pointsVisible: false
        width: 4
        axisX: ValueAxis{
            id: xAxis
            min: 0
            max: 10000
            tickCount: 10
            minorTickCount: 9
            labelFormat:"%.1f min"
        }
        axisY: ValueAxis{
            id: yAxis
            min: 0
            max: 10000
            tickCount: 10
            labelFormat:"%d ft/min"
        }
    }

    LineSeries {
        id: secondSeries
        name: std ? "IVV" : "Threshold"
        color: "red"
        style: std ? 1 : 2 // Qt.SolidLine : Qt.DashLine
        pointsVisible: false
        width: 4
        axisX: xAxis
        axisY: yAxis
    }

    function update() {
        console.info("Displaying", title)
        let maxWindows = 0
        if (std) {
            let maxBar = 0, maxIvv = 0, minBar = 0, minIvv = 0
            for (let index = 0; index < windows.length; index++) {
                Util.appendVerticalLine(windows[index], bar[index], series)
                Util.appendVerticalLine(windows[index], ivv[index], secondSeries)

                maxWindows = Math.max(maxWindows, windows[index])
                maxBar = Math.max(maxBar, bar[index])
                maxIvv = Math.max(maxIvv, ivv[index])
                minBar = Math.min(minBar, bar[index])
                minIvv = Math.min(minIvv, ivv[index])
            }

            yAxis.max = Util.nextMultipleOf5(Math.max(maxBar, maxIvv))
            yAxis.min = Util.nextMultipleOf5(Math.min(minBar, minIvv), false)

        } else {
            secondSeries.append(0, threshold)
            secondSeries.append(windows[windows.length -1], threshold)
            let maxDiff = 0, minDiff = 0
            for (let index = 0; index < windows.length; index++) {
                Util.appendVerticalLine(windows[index], diff[index], series)

                maxWindows = Math.max(maxWindows, windows[index])
                maxDiff = Math.max(maxDiff, diff[index])
                minDiff = Math.min(minDiff, diff[index])
            }

            yAxis.max = Util.nextMultipleOf5(maxDiff)
            yAxis.min = Util.nextMultipleOf5(minDiff, false)
        }

        xAxis.max = Util.nextMultipleOf5(maxWindows)

        xAxis.applyNiceNumbers()
        yAxis.applyNiceNumbers()
    }

    onThresholdChanged: update()
}
