import QtQuick 2.15
import QtQuick.Controls 2.15
import QtLocation 5.15
import QtPositioning 5.15
import Qt.labs.location 1.0
import QtQml.Models 2.15
import "qrc:/scripts/constants.js" as Constants

Frame {
    id: rootFrame
    property var location: __mode_s.partialLocationSeries
    property var turbulentLocation: __mode_s.partialTurbulentSeries
    property var kde: __mode_s.partialHeatMapSeries

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
    signal kdeClicked(double latitude, double longitude, double bandwidth, string zoneID)

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

    function updateAllViews() {
        locationGroup.clear()
        turbulentGroup.clear()
        kdeGroup.clear()
        
        map.clearMapItems()

        locationLoader.start()
        turbulentLoader.start()
        kdeLoader.start()

    }

    function update(view) {
        switch (view) {
            case Constants.LOCATION:
                if(location.length > 0) {
                    locationGroup.clear()
                }
                locationLoader.start()
                break
            case Constants.TURBULENCE:
                if(turbulentLocation.length > 0) {
                    turbulentGroup.clear()
                }
                turbulentLoader.start()
                break
            case Constants.KDE:
                if(turbulentLocation.length > 0) {
                    kdeGroup.clear()
                }
                kdeLoader.start()
                break
        }
    }

    Timer {
        id: locationLoader
        interval: 11500
        running: false
        repeat: true
        triggeredOnStart: false
        property string progressID: Constants.ID_LOCATION
        property int counter: 0
        property int maxSegmentLength: 500
        property var source: location
        property var target: locationGroup
        property string sourceStr: "location"
        onTriggered: {
            run(locationLoader)
        }
    }
    
    Timer {
        id: turbulentLoader
        interval: 2000
        running: false
        repeat: true
        triggeredOnStart: false
        property string progressID: Constants.ID_TURBULENT
        property int counter: 0
        property int maxSegmentLength: 20
        property var source: turbulentLocation
        property var target: turbulentGroup
        property string sourceStr: "turbulence"
        onTriggered: {
            run(turbulentLoader)
        }
    }

    Timer {
        id: kdeLoader
        interval: 1250
        running: false
        repeat: true
        triggeredOnStart: false
        property string progressID: Constants.ID_KDE
        property int counter: 0
        property int maxSegmentLength: 10
        property var source: kde
        property var target: kdeGroup
        property string sourceStr: "kde"
        onTriggered: {
            run(kdeLoader)
        }
    }

    function run(timer) {
        let endSlice = __mode_s.preparePartialSeries(timer.sourceStr, timer.counter, timer.maxSegmentLength)
        let partialList = timer.source

        if (endSlice < 0) {
            timer.counter = 0
            timer.stop()
            return
        }

        timer.counter = endSlice
        mapWorker.sendMessage({"type": timer.sourceStr, "target": timer.target, "listPoint": partialList})
    }
    
    MMenuBar {
        id: menubar
        z: 1
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

        MouseArea{
            anchors.fill: parent
            z: -1
            cursorShape: Qt.OpenHandCursor
            hoverEnabled: true
            onPressed: cursorShape = Qt.ClosedHandCursor
            onCanceled: cursorShape = Qt.ClosedHandCursor
            onPositionChanged: cursorShape = Qt.OpenHandCursor
            onReleased: cursorShape = Qt.OpenHandCursor
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
            mapElementInfo.address = `Field width: ${kdeZone.fieldwidth.toFixed(1)} km`
            mapElementInfo.flightColor = kdeZone.color
            mapElementInfo.displayText = "Num. of Fligths"
            mapElementInfo.datapoints = kdeZone.numFligths
            mapElementInfo.turbulentFlight = true
            mapElementInfo.buttonShowGraph = false
            mapElementInfo.open()
            rootFrame.kdeClicked(kdeZone.centerLatitude, kdeZone.centerLongitude, kdeZone.bw, kdeZone.zoneID)
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
            tlLon: topLeftLon
            tlLat: topLeftLat
            brLon: bottomRightLon
            brLat: bottomRightLat
            bw: bandwidth
            zoneID: kdeZoneID
            numFligths: numOfAddresses
            fieldwidth: fieldWidth
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
