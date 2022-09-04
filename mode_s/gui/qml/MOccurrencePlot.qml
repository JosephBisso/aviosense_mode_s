import QtQuick 2.15
import QtCharts 2.15

ChartView {
    id: chartView

    axes: [
        ValueAxis{
            id: xAxis
            min: 0
            max: 10000
            labelFormat:"%d Addresses"
        },
        ValueAxis{
            id: yAxis
            min: 0
            max: 10000
            labelFormat:"%d Data Points"
        }
    ]

    Connections {
        target: __mode_s

        function onPlotOccurrenceReady() {
            console.info("Displaying line series for occurrences")
            chartView.removeAllSeries()
            let pointList = __mode_s.occurrenceSeries
            if (__mode_s.occurrenceSeries.length == 0) {return}
            var series = chartView.createSeries(ChartView.SeriesTypeLine, "Datapoints over addresses", xAxis, yAxis)
            series.pointsVisible = true
            // series.hovered.connect((point, state) => { console.log("hovered", point, state);})

            for (let index = 0; index < pointList.length; index++) {
                series.append(index+1, pointList[index])
            }

            xAxis.max = pointList.length
            yAxis.max = Math.max.apply(null, pointList)
            xAxis.applyNiceNumbers()
            yAxis.applyNiceNumbers()
        }
    } 
}
