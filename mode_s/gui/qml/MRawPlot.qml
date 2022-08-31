import QtCharts 2.15
import QtQml 2.15
import "qrc:/scripts/plot.js" as PLT

ChartView {
    id: chartView
    property var bar: []
    property var ivv: []
    property var time: []
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
        id: barSeries
        name: "BAR"
        color: "blue"
        width: 1
        pointsVisible: true
    }

    LineSeries {
        id: ivvSeries
        name: "IVV"
        color: "red"
        width: 1
        pointsVisible: true
    }

    function update() {
        console.info("Displaying", title)
        for (let index = 0; index < time.length; index++) {
            barSeries.append(time[index], bar[index])
            ivvSeries.append(time[index], ivv[index])
        }
        let maxBar = Math.max.apply(null, bar)
        let maxIvv = Math.max.apply(null, ivv)
        let minBar = Math.min.apply(null, bar)
        let minIvv = Math.min.apply(null, ivv)
        xAxis.max = Math.max.apply(null, time)
        yAxis.max = Math.max(maxBar, maxIvv)
        xAxis.min = Math.min.apply(null, time)
        yAxis.min = Math.min(maxBar, maxIvv)
        xAxis.applyNiceNumbers()
        yAxis.applyNiceNumbers()
    }

    onTimeChanged: update()
}
