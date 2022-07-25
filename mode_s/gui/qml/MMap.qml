import QtQuick 2.15
import QtQuick.Controls 2.15
import QtLocation 5.15
import QtPositioning 5.15
import Qt.labs.location 1.0
import QtQml.Models 2.15
import "qrc:/scripts/Constants.js" as Constants

Frame {
    id: rootFrame
    property var location: []
    property var turbulentLocation: []
    property var kde: []
    property bool locationView: true

    property string mode: "LOC"

    ListModel{id: locationGroup}
    ListModel{id: turbulentGroup}
    ListModel{id: kdeGroup}

    background: Rectangle {
        color: "transparent"
        border.color: Constants.BACKGROUND_COLOR2
        radius: 10
    }
    signal done()
    signal addressClicked(int address)

    function showLocation() {
        mapWorker.sendMessage({"type": "location", "target": locationGroup, "listPoint": location})
    }
    function prepareTurbulentLocation(){  
        mapWorker.sendMessage({"type": "turbulent", "target": turbulentGroup, "listPoint": turbulentLocation})
    }
    function prepareKDE(){ 
        mapWorker.sendMessage({"type": "kde", "target": kdeGroup, "listPoint": kde})
    }

    MMenuBar {
        id: menubar
        z: 1
        width: 225
        anchors{
            bottom: parent.bottom
            horizontalCenter: parent.horizontalCenter

            topMargin: 10
        }
        models: ListModel  {
            ListElement {
                name: "LOC"
                fullName: "Location"
            }
            ListElement {
                name: "TRB"
                fullName: "Turbulent Location"
            }
            ListElement {
                name: "KDE"
                fullName: "Kernel Density Estimation"
            }
        }

        onClicked: (element) => {rootFrame.updateView(element)}
    }

    Map {
        id: map
        property var lastPolylineClicked
        property var actualAddress
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


        function addressClicked(polyline, address) {
            showPolyline(polyline)
            rootFrame.addressClicked(address)
        }

        function showPolyline(polyline) {
            if (lastPolylineClicked) {lastPolylineClicked.reset()}
            polyline.show()
            map.lastPolylineClicked = polyline
        }

    }

    Instantiator {
        id: instantiator
        asynchronous: true
        active: true
        model: rootFrame.mode === "TRB" ? turbulentGroup : locationGroup 
        delegate: MMapPolyline {
            id: locationDelegate
            address: location_address
            identification: location_identification
            lineColor: rootFrame.mode === "TRB" ? "red" : Qt.rgba(r, g, b, 1)
            path: {
                let allPoints = []
                for (let i = 0; i < segment.count; i++) {
                    allPoints.push(segment.get(i))
                }
                return allPoints
            }
        }

        onObjectAdded: {
            map.addMapItem(object)
        }
    }

    Instantiator {
        id: instantiatorTurbulent
        asynchronous: true
        active: false
        model: turbulentGroup
        delegate: MMapPolyline {
            id: turbulentDelegate
            address: location_address
            identification: location_identification
            lineColor: "red"
            path: {
                let allPoints = []
                for (let i = 0; i < segment.count; i++) {
                    allPoints.push(segment.get(i))
                }
                return allPoints
            }
        }

        onObjectAdded: {
            map.addMapItem(object)
        }
    }

    WorkerScript {
        id: mapWorker
        source: "qrc:/scripts/map.js"

        onMessage: {
            console.log("Gui Thread: Done ", messageObject.toLoad)
        }
    }

    function showAddress(address) {
        map.actualAddress = address
    }

    function updateView(name) {
        switch (name) {
            case "LOC":
            map.clearMapItems()
            rootFrame.mode = "LOC"
            instantiator.active = true
                break;
            case "TRB":
            map.clearMapItems()
            rootFrame.mode = "TRB"
            instantiator.active = true
                break;
            case "KDE":
            map.clearMapItems()
            rootFrame.mode = "KDE"
            locationView = false
            // instantiator.model = locationGroup
                break;
        }
    }

}
