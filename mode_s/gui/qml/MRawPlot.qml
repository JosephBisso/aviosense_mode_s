import QtCharts 2.15
import QtQml 2.15
import "qrc:/scripts/util.js" as Util

ChartView {
    id: chartView
    property var bar: []
    property var ivv: []
    property var time: []
    property string address: ""
    property string identification: ""
    animationOptions: ChartView.SeriesAnimations

    MZoomableArea {
        control: chartView
    }

    LineSeries {
        id: barSeries
        name: "BAR"
        color: "blue"
        width: 1
        pointsVisible: true
        axisX: xAxis
        axisY: yAxis
    }

    LineSeries {
        id: ivvSeries
        name: "IVV"
        color: "red"
        width: 1
        pointsVisible: true
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
            labelFormat:"%d ft/min"
        }
    }

    function update() {
        console.info("Displaying", title)
        let maxBar = 0, maxIvv = 0, minBar = 0, minIvv = 0, maxTime = 0
        for (let index = 0; index < time.length; index++) {
            barSeries.append(time[index], bar[index])
            ivvSeries.append(time[index], ivv[index])

            maxTime = Math.max(maxTime, time[index])
            maxBar = Math.max(maxBar, bar[index])
            maxIvv = Math.max(maxIvv, ivv[index])
            minBar = Math.min(minBar, bar[index])
            minIvv = Math.min(minIvv, ivv[index])
        }
        xAxis.max = Util.nextMultipleOf5(maxTime)
        yAxis.max = Util.nextMultipleOf5(Math.max(maxBar, maxIvv))
        yAxis.min = Util.nextMultipleOf5(Math.min(minBar, minIvv), false)

        xAxis.applyNiceNumbers()
        yAxis.applyNiceNumbers()
    }

    onTimeChanged: update()
}
