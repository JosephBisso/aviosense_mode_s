import QtQuick
import QtCharts 

ChartView {
    id: chartView
    antialiasing: true

    Connections {
        target: __mode_s

        function onReadyToPlot() {
            chartView.setChart(__mode_s.plot(title))
        }
    } 
}
