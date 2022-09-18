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
    signal addressClicked(int address, string mode)
    signal kdeClicked(double latitude, double longitude, double bandwidth)

    function stopBackgroundLoading(progressID) {
        switch (progressID) {
            case Constants.ID_LOCATION:
                locationLoader.counter = 0
                locationLoader.stop()
                break
            case Constants.ID_TURBULENT:
                turbulentLoader.counter = 0
                turbulentLoader.stop()
                break
            case Constants.ID_KDE:
                kdeLoader.counter = 0
                kdeLoader.stop()
                break

        }
        console.info(Constants.PROGRESS_BAR, progressID, Constants.END_PROGRESS_BAR)
    }
    function pauseBackgroundLoading() {
        locationLoader.stop()
        turbulentLoader.stop()
        kdeLoader.stop()
    }
    function resumeBackgroundLoading() {
        locationLoader.start()
        turbulentLoader.start()
        kdeLoader.start()
    }

    function update(view) {
        switch (view) {
            case Constants.LOCATION:
                if(location.length > 0) {
                    console.log(location.length)
                    locationGroup.clear()
                    locationLoader.start()
                }
                break
            case Constants.TURBULENCE:
                if(turbulentLocation.length > 0) {
                    turbulentGroup.clear()
                    turbulentLoader.start()
                }
                break
            case Constants.KDE:
                if(turbulentLocation.length > 0) {
                    kdeGroup.clear()
                    kdeLoader.start()
                }
                break
        }
    }

    Timer {
        id: locationLoader
        interval: 15000
        running: false
        repeat: true
        triggeredOnStart: false
        property string progressID: Constants.ID_LOCATION
        property int counter: 0
        property int maxSegmentLength: 500
        property var source: location
        property var target: locationGroup
        property string sourceStr: "location"
        property string progressString: "Loading All Routes"
        onTriggered: {
            run(locationLoader)
        }
    }
    Timer {
        id: turbulentLoader
        interval: 1500
        running: false
        repeat: true
        triggeredOnStart: false
        property string progressID: Constants.ID_TURBULENT
        property int counter: 0
        property int maxSegmentLength: 20
        property var source: turbulentLocation
        property var target: turbulentGroup
        property string sourceStr: "turbulent"
        property string progressString: "Loading All Turbulent Routes"
        onTriggered: {
            run(turbulentLoader)
        }
    }

    Timer {
        id: kdeLoader
        interval: 1000
        running: false
        repeat: true
        triggeredOnStart: false
        property string progressID: Constants.ID_KDE
        property int counter: 0
        property int maxSegmentLength: 10
        property var source: kde
        property var target: kdeGroup
        property string sourceStr: "kde"
        property string progressString: "Loading All KDE Zones"
        onTriggered: {
            run(kdeLoader, true)
        }
    }

    function run(t, kde=false) {
        console.info(Constants.PROGRESS_BAR, t.progressID, `${t.progressString} [${t.counter}/${t.source.length - 1}]`)
        let endSlice = 0
        let partialList = []

        if (kde) {
            endSlice = t.counter + t.maxSegmentLength
            partialList = t.source.slice(t.counter, endSlice )
        } else {
            let actualSegmentLength = t.source[t.counter].segments.length
            endSlice = t.counter + 1
            while (endSlice <= t.source.length - 1 && actualSegmentLength + t.source[endSlice].segments.length < t.maxSegmentLength) {
                actualSegmentLength += t.source[endSlice].segments.length
                endSlice++
            }
            console.log(`Loading ${actualSegmentLength} ${t.sourceStr} elements`)
            partialList = t.source.slice(t.counter, endSlice)
        }
        
        mapWorker.sendMessage({"type": t.sourceStr, "target": t.target, "listPoint": partialList})
        t.counter = endSlice
        if (t.counter >= t.source.length - 1) {
            console.info(Constants.PROGRESS_BAR, t.progressID, Constants.END_PROGRESS_BAR)
            t.counter = 0
            t.stop()
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
            rootFrame.addressClicked(address, rootFrame.mode)
        }

        function zoneKDEClicked(kdeZone) {
            mapElementInfo.identification = `${kdeZone.centerLatitude.toFixed(2)}N, ${kdeZone.centerLongitude.toFixed(2)}E`
            mapElementInfo.address = `Offset: +/-${(kdeZone.bw / 2).toFixed(2)}`
            mapElementInfo.flightColor = kdeZone.color
            mapElementInfo.displayText = "KDE"
            mapElementInfo.datapoints = kdeZone.kde_e.toFixed(2)
            mapElementInfo.turbulentFlight = true
            mapElementInfo.buttonShowGraph = false
            mapElementInfo.open()
            rootFrame.kdeClicked(kdeZone.centerLatitude, kdeZone.centerLongitude, kdeZone.bw)
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
            mapElementInfo.buttonShowGraph = true
            mapElementInfo.mode = rootFrame.mode
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
