import QtQuick 2.15
import QtQuick.Controls 2.15
import QtLocation 5.15
import QtPositioning 5.15
import Qt.labs.location 1.0
import QtQml.Models 2.15
import "qrc:/scripts/Constants.js" as Constants

Frame {
    id: rootFrame
    property real radius: 10000
    property var location: []
    property var turbulentLocation: []
    property var kde: []

    property var locationGroup: []
    property var turbulentGroup: []
    property var kdeGroup: []

    background: Rectangle {
        color: "transparent"
        border.color: Constants.BACKGROUND_COLOR2
        radius: 10
    }

    MMenuBar {
        id: menubar
        z: 1
        width: 225
        models: ["LOC", "TUR", "KDE"]
        anchors{
            bottom: parent.bottom
            horizontalCenter: parent.horizontalCenter

            topMargin: 10
        }

        onClicked: (element) => {updateView(element)}
    }

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

    MapItemGroup {
        id: group
    }

    function updateView(name) {
        switch(name) {
            case "LOC":
                break;
            case "TRB":
                break;
            case "KDE":
                break;
        }
    }   
    
    function addPolyline(segment, r, g, b, target) {
        let allPoints = []
        for (let k = 0; k < segment.length; k++) {
            allPoints.push(QtPositioning.coordinate(segment[k].latitude, segment[k].longitude))
        }
        var component = Qt.createComponent("MMapPolyline.qml")
        var polyLine = component.createObject(group, {
            address     : segment[0].address,
            lineColor   : Qt.rgba(r, g, b, 1),
            path        : allPoints
        })
        if (target === "location") {
            locationGroup.push(polyLine)
        } else {
            turbulentGroup.push(polyLine)
        }    
    }

    function showLocation() {
        console.info("Displaying line series for location")
        map.clearMapItems()
        group.children = []
        locationGroup = []
        let usedColors = []

        for (let i = 0; i < rootFrame.location.length; i++) {
            let r, b, g, colorStr
            do {
                r = Math.random()
                g = Math.random()
                b = Math.random()
                colorStr = `r${r}g${g}b${b}`
            } while (usedColors.includes(colorStr))

            usedColors.push(colorStr)

            var segment = []

            let address = rootFrame.location[i].address
            let lat0 = rootFrame.location[i].points[0].latitude
            let long0 = rootFrame.location[i].points[0].longitude
            segment.push({"longitude": long0, "latitude": lat0, "address": address})

            for (let j = 1; j < rootFrame.location[i].points.length; j++) {
                let latitude = rootFrame.location[i].points[j].latitude
                let longitude = rootFrame.location[i].points[j].longitude

                var point = QtPositioning.coordinate(latitude, longitude)
                let lastSegmentIndex = segment.length - 1
                let lastSegmetPoint = QtPositioning.coordinate(segment[lastSegmentIndex].latitude, segment[lastSegmentIndex].longitude)
                if (lastSegmetPoint.distanceTo(point) < rootFrame.radius) {
                    segment.push({"longitude": point.longitude, "latitude": point.latitude, "address": address})
                    if (j == rootFrame.location[i].points.length - 1) {
                        rootFrame.addPolyline(segment, r, g, b, "location")
                    }
                } else {
                    rootFrame.addPolyline(segment, r, g, b, "location")
                    segment = []
                    segment.push({"longitude": point.longitude, "latitude": point.latitude, "address": address})
                }
            }
        }

        map.addMapItemGroup(group)
    }
}
