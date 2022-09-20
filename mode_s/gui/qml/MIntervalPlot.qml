import QtCharts 2.15
import QtQml 2.15
import "qrc:/scripts/util.js" as Util

ChartView {
    id: chartView
    property var points: []
    property var windows: []
    property string address: ""
    property string identification: ""

    LineSeries {
        id: slidingSeries
        name: "Slidings Windows"
        color: "blue"
        width: 4
        axisX: ValueAxis{
            id: xAxis
            min: 0
            max: 10000
            tickCount: 10
            labelFormat:"%.1f min"
        }
        axisY: ValueAxis{
            id: yAxis
            min: 0
            max: 10000
            tickCount: 10
            labelFormat:"%d points"
        }
    }

    function update() {
        console.info("Displaying", title)
        let maxWindows = 0, maxPoints = 0
        for (let index = 0; index < windows.length; index++) {
            let middleWindows = windows[index]
            if (index > 0) {
                middleWindows = (windows[index] + windows[index-1]) / 2
                slidingSeries.append(middleWindows, points[index-1])
            }
            slidingSeries.append(middleWindows, points[index])

            maxWindows = Math.max(maxWindows, windows[index])
            maxPoints = Math.max(maxPoints, points[index])
        }
        xAxis.max = Util.nextMultipleOf5(maxWindows)
        yAxis.max = Util.nextMultipleOf5(maxPoints + Math.round(maxPoints/10))

        xAxis.applyNiceNumbers()
        yAxis.applyNiceNumbers()
    }

    onWindowsChanged: update()
}
