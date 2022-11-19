
import QtCharts 2.15
import QtQml 2.15
import "qrc:/scripts/util.js" as Util

ChartView {
    id: chartView
    property string dataSet: ""
    property var raw: []
    property var filtered: []
    property var time: []
    property string address: ""
    property string identification: ""
    animationOptions: ChartView.SeriesAnimations

    MZoomableArea {
        control: chartView
    }

    LineSeries {
        id: rawSeries
        name: "RAW " + chartView.dataSet
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

    LineSeries {
        id: filteredSeries
        name: "FILTERED " + chartView.dataSet
        color: chartView.dataSet === "BAR" ? "blue" : "darkturquoise"
        width: 1
        pointsVisible: true
        axisX: xAxis
        axisY: yAxis

    }

    function update() {
        console.info("Displaying", title)
        let maxRaw = 0, maxFiltered = 0, minRaw = 0, minFiltered = 0, maxTime = 0
        for (let index = 0; index < time.length; index++) {
            rawSeries.append(time[index], raw[index])
            filteredSeries.append(time[index], filtered[index])

            maxTime = Math.max(maxTime, time[index])
            maxRaw = Math.max(maxRaw, raw[index])
            maxFiltered = Math.max(maxFiltered, filtered[index])
            minRaw = Math.min(minRaw, raw[index])
            minFiltered = Math.min(minFiltered, filtered[index])

        }
        xAxis.max = Util.nextMultipleOf5(maxTime)
        yAxis.max = Util.nextMultipleOf5(Math.max(maxRaw, maxFiltered))
        yAxis.min = Util.nextMultipleOf5(Math.min(minRaw, minFiltered), false)

        xAxis.applyNiceNumbers()
        yAxis.applyNiceNumbers()
    }

    onTimeChanged: update()
}
