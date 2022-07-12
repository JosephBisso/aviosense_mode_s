
import QtCharts 2.15

ChartView {
    id: chartView
    property string dataSet: ""
    property var raw: []
    property var filtered: []
    property var time: []

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
        id: rawSeries
        name: "RAW " + chartView.dataSet
        color: "red"
    }

    LineSeries {
        id: filteredSeries
        name: "FILTERED " + chartView.dataSet
        color: chartView.dataSet === "BAR" ? "blue" : "darkturquoise"
    }

    onTimeChanged: {
        for (let index = 0; index < time.length; index++) {
            rawSeries.append(time[index], raw[index])
            filteredSeries.append(time[index], filtered[index])
        }
        let maxRaw = Math.max.apply(null, raw)
        let maxFiltered = Math.max.apply(null, filtered)
        let minRaw = Math.min.apply(null, raw)
        let minFiltered = Math.min.apply(null, filtered)
        xAxis.max = Math.max.apply(null, time)
        yAxis.max = Math.max(maxRaw, maxFiltered)
        xAxis.min = Math.min.apply(null, time)
        yAxis.min = Math.min(maxRaw, maxFiltered)
        xAxis.applyNiceNumbers()
        yAxis.applyNiceNumbers()
    }
}
