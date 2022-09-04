import QtQuick 2.15
import QtQuick.Controls 2.15
import QtLocation 5.15
import QtPositioning 5.15
import Qt.labs.location 1.0
import QtQml.Models 2.15
import "qrc:/scripts/Constants.js" as Constants

Frame {
    id: rootFrame
    property var location: __mode_s.locationSeries
    property var turbulentLocation: __mode_s.turbulentLocationSeries
    property var kde: __mode_s.heatMapSeries

    property string mode: Constants.LOCATION
    property bool locationView: rootFrame.mode !== Constants.KDE

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

    function stopBackgroundLoading() {
        locationUpdater.counter = 0
        locationUpdater.stop()
    }
    function pauseBackgroundLoading() {
        locationUpdater.stop()
    }
    function resumeBackgroundLoading() {
        locationUpdater.start()
    }

    function update(view) {
        let type = "location"
        let target = locationGroup
        let pointList = location

        target.clear()

        switch (view) {
            case Constants.LOCATION:
                if(location.length > 0) locationUpdater.start()
                return
            case Constants.TURBULENCE:
                type        = "turbulent"
                target      = turbulentGroup
                pointList   = turbulentLocation
                break
            case Constants.KDE:
                type        = "kde"
                target      = kdeGroup
                pointList   = kde
                break
        }

        if (pointList.length === 0) {return}
        mapWorker.sendMessage({"type": type, "target": target, "listPoint": pointList}) 
    }

    Timer {
        id: locationUpdater
        interval: 10000
        running: false
        repeat: true
        triggeredOnStart: false
        property int counter: 0
        property int maxSegmentLength: 1000
        onTriggered: {
            let actualSegmentLength = location[counter].segments.length
            let endSlice = counter + 1
            while (actualSegmentLength + location[endSlice].segments.length < maxSegmentLength) {
                actualSegmentLength += location[endSlice].segments.length
                endSlice++
            }
            let partialList = location.slice(counter, endSlice)
            mapWorker.sendMessage({"type": "location", "target": locationGroup, "listPoint": partialList})
            counter = endSlice
            if (counter > location.length - 1) {
                counter = 0
                locationUpdater.stop()
            }
        }
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

        onActualAddressChanged: markPolyline(actualAddress)

        function markPolyline(targetAddress) {
            let targetInstantiator = rootFrame.mode === Constants.TURBULENCE ? instantiatorTurbulent : instantiator 
            let turbulence = false

            for (let i = 0; i < targetInstantiator.count; i++) {
                if (!targetInstantiator.objectAt(i)){continue;}
                if (targetInstantiator.objectAt(i).address != targetAddress) {continue;}
                showPolyline(targetInstantiator.objectAt(i))
                if (rootFrame.mode === Constants.TURBULENCE) {turbulence = true}
                else {
                    for (let j = 0; j < turbulentGroup.count; j++) {
                        if (turbulentGroup.get(j).location_address != targetAddress) {continue;}
                        turbulence = true
                        break
                    }
                }
                showFlightInfo(targetInstantiator.objectAt(i), turbulence)
                break
            }
        }

        function addressClicked(polyline, address) {
            showPolyline(polyline)
            let turbulence = false
            if (rootFrame.mode === Constants.TURBULENCE) {turbulence = true}
            else {
                for (let j = 0; j < turbulentGroup.count; j++) {
                    if (turbulentGroup.get(j).location_address != polyline.address) {continue;}
                    turbulence = true
                    break
                }
            }
            showFlightInfo(polyline, turbulence)
            rootFrame.addressClicked(address)
        }

        function zoneKDEClicked(kdeZone) {
            mapElementInfo.identification = `${kdeZone.centerLatitude.toFixed(2)}N, ${kdeZone.centerLongitude.toFixed(2)}E`
            mapElementInfo.address = `Bandwidth: ${kdeZone.bw}`
            mapElementInfo.flightColor = kdeZone.color
            mapElementInfo.displayText = `KDE (tat.)\t: ${kdeZone.kde_e.toFixed(2)}\nKDE (%max)\t`
            mapElementInfo.datapoints = kdeZone.kde_normed.toFixed(2) * 100
            mapElementInfo.turbulentFlight = true
            mapElementInfo.showButton = false
            mapElementInfo.open()
        }

        function showPolyline(polyline) {
            if (lastPolylineClicked) {lastPolylineClicked.reset()}
            polyline.show()
            map.lastPolylineClicked = polyline
        }

        function showFlightInfo(polyline, turbulent) {
            mapElementInfo.identification = polyline.identification
            mapElementInfo.address = polyline.address
            mapElementInfo.flightColor = polyline.lineColor
            mapElementInfo.displayText = "Data points"
            mapElementInfo.datapoints = polyline.path.length
            mapElementInfo.turbulentFlight = turbulent
            mapElementInfo.showButton = true
            mapElementInfo.open()
        }

    }

    Instantiator {
        id: instantiator
        asynchronous: true
        active: rootFrame.locationView && rootFrame.mode === Constants.LOCATION
        model: locationGroup 
        delegate: MMapPolyline {
            id: locationDelegate
            address: location_address
            identification: location_identification
            lineColor: Qt.rgba(r, g, b, 1)
            path: {
                let allPoints = []
                for (let i = 0; i < segment.count; i++) {
                    allPoints.push(segment.get(i))
                }
                return allPoints
            }
        }

        onObjectAdded: {
            if (active) {
                map.addMapItem(object)
            }
        }

        onObjectRemoved: {
            map.removeMapItem(object)
        }
    }

    Instantiator {
        id: instantiatorTurbulent
        asynchronous: true
        active: rootFrame.locationView && rootFrame.mode === Constants.TURBULENCE
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
            if (active) {
                map.addMapItem(object)
            }
        }
        onObjectRemoved: {
            map.removeMapItem(object)
        }

    }

    Instantiator {
        id: instantiatorKDE
        asynchronous: true
        active: !rootFrame.locationView && rootFrame.mode === Constants.KDE
        model: kdeGroup
        delegate: MMapRectangle {
            id: kdeDelegate
            kde_e: kde
            kde_normed: normedKDE
            centerLatitude: latitude
            centerLongitude: longitude
            bw: bandwidth
        }

        onObjectAdded: {
            if (active) {
                map.addMapItem(object)
            }
        }
        onObjectRemoved: {
            map.removeMapItem(object)
        }

    }

    WorkerScript {
        id: mapWorker
        source: "qrc:/scripts/map.js"

        onMessage: {
            console.log("Map Worker: Done ", messageObject.toLoad)
        }
    }

    function showAddress(address) {
        map.actualAddress = address
    }

    function updateView(name) {
        if (rootFrame.mode === name) {return}
        switch (name) {
            case Constants.LOCATION:
                map.clearMapItems()
                rootFrame.mode = Constants.LOCATION
                break;
            case Constants.TURBULENCE:
                map.clearMapItems()
                rootFrame.mode = Constants.TURBULENCE
                break;
            case Constants.KDE:
                map.clearMapItems()
                rootFrame.mode = Constants.KDE
                break;
        }
    }

}
