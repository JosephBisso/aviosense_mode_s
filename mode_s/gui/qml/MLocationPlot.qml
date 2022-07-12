import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import QtLocation 5.15
import QtPositioning 5.6

Frame {
    anchors.fill: parent
    Map {
        id: map
        anchors.fill: parent
        center: QtPositioning.coordiante(60, 11)
        zoomLevel: 14
        plugin : Plugin {name: "mapboxgl"}
        
        MapParameter {
            type: "source"

            property var name: "root"
            property var sourceType: "geojson"
            property var data: "qrc:/scripts/world.geojson"
        }

    }
    
}

// ChartView {
//     id: chartView
//     axes: [
//         ValueAxis{
//             id: xAxis
//             min: 0
//             max: 10000
//             labelFormat:"%d Addresses"
//         },
//         ValueAxis{
//             id: yAxis
//             min: 0
//             max: 10000
//             labelFormat:"%d Data Points"
//         }
//     ]

//     Connections {
//         target: __mode_s

//         function onPlotLocationReady(pointList) {
//             chartView.removeAllSeries()
//             var series = chartView.createSeries(ChartView.SeriesTypeLine, "Location", xAxis, yAxis)
//             series.pointsVisible = true
//             // series.hovered.connect((point, state) => { console.log("hovered", point, state);})

//             for (let index = 0; index < pointList.length; index++) {
//                 series.append(index+1, pointList[index])
//             }

//             xAxis.max = pointList.length
//             yAxis.max = Math.max.apply(null, pointList)
//             xAxis.applyNiceNumbers()
//             yAxis.applyNiceNumbers()
//         }
//     } 
// }
