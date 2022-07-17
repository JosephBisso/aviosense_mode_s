import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import QtLocation 5.15
import QtPositioning 5.15
import Qt.labs.location 1.0
import QtQml.Models 2.15

Frame {
    id: rootLocation
    property real radius: 20000
    Map {
        id: map
        anchors.fill: parent
        activeMapType: map.supportedMapTypes[0]
        center: QtPositioning.coordinate(51, 10)
        zoomLevel: 6
        plugin: Plugin {
            name: 'osm'
            PluginParameter {
                name: "osm.mapping.providersrepository.disabled"
                value: "true"
            }
            PluginParameter {
                name: "osm.mapping.providersrepository.address"
                value: "http://maps-redirect.qt.io/osm/5.6/"
            }
        }

    }
    
    function addPolyline(segment, r, g, b) {
        let allPoints = []
        for (let k = 0; k < segment.length; k++) {
            allPoints.push(`{longitude:${segment[k].longitude}, latitude:${segment[k].latitude}}`)
        }
        var polyLine = Qt.createQmlObject(
           `import QtLocation 5.15
            MapPolyline {
                line.width:5
                line.color: Qt.rgba(${r}, ${g}, ${b}, 1)
                path:[${allPoints.toString()}]
            }`,
            rootLocation
        )

        map.addMapItem(polyLine)
    }

    function showRoutes (pointList) {
        console.info("Displaying line series for location")
        map.clearMapItems()
        let usedColors = []

        for (let i = 0; i < pointList.length; i++) {
            let r, b, g, colorStr
            do {
                r = Math.random()
                g = Math.random()
                b = Math.random()
                colorStr = `r${r}g${g}b${b}`
            } while (usedColors.includes(colorStr))

            usedColors.push(colorStr)

            var addressData = {
                "address"   : pointList[i].address,
            }

            var segment = []

            let lat0 = pointList[i].points[0].latitude
            let long0 = pointList[i].points[0].longitude
            segment.push({"longitude": long0, "latitude": lat0})

            for (let j = 1; j < pointList[i].points.length; j++) {
                let latitude = pointList[i].points[j].latitude
                let longitude = pointList[i].points[j].longitude

                var point = QtPositioning.coordinate(latitude, longitude)
                let lastSegmentIndex = segment.length - 1
                let lastSegmetPoint = QtPositioning.coordinate(segment[lastSegmentIndex].latitude, segment[lastSegmentIndex].longitude)
                if (lastSegmetPoint.distanceTo(point) < rootLocation.radius) {
                    segment.push({"longitude": point.longitude, "latitude": point.latitude})
                    if (j == pointList[i].points.length - 1) {
                        rootLocation.addPolyline(segment, r, g, b)
                    }
                } else {
                    rootLocation.addPolyline(segment, r, g, b)
                    segment = []
                    segment.push({"longitude": point.longitude, "latitude": point.latitude})
                }
            }
        }
    }
}
