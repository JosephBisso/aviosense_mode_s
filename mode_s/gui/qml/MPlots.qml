import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import QtQml 2.15
import "qrc:/scripts/constants.js" as Constants

Frame {
    id: plotFrame
    property bool isCurrentView: false
    property alias swipe: plotSwipe

    background: Rectangle {
        color: "transparent"
        border.color: Constants.BACKGROUND_COLOR2
        radius: 10
    }

    function updateView(name) {
        switch(name) {
            case "OCC":
                plotView.swipe.currentIndex = 0
                break;
            case "RAW":
                plotView.swipe.currentIndex = 1
                break;
            case "FIL":
                plotView.swipe.currentIndex = 2
                break;
            case "INT":
                plotView.swipe.currentIndex = 3
                break;
            case "STD":
                plotView.swipe.currentIndex = 4
                break;
            case "EXD":
                plotView.swipe.currentIndex = 5
                break;
            case "KDE":
                plotView.swipe.currentIndex = 6
                break;
        }
    }   

    function preparePlotsForAddress(address, mode) {
        if (plotSwipe.currentAddress != address) {
            __mode_s.prepareAddress(address)   
            plotSwipe.currentAddress = address
        }
        plotSwipe.mode = mode
        if(plotFrame.isCurrentView){plotBackgroundLoader.startLoading()}
    }

    function prepareKDEExceedZone(latitude, longitude, bandwidth, zoneID) {
        if (plotSwipe.kdeZoneLatitude != latitude && plotSwipe.kdeZoneLongitude != longitude
                && plotSwipe.kdeZoneBandwidth != bandwidth) {
            __mode_s.prepareKDEZone(zoneID)
            plotSwipe.kdeZoneLatitude = latitude
            plotSwipe.kdeZoneLongitude = longitude
            plotSwipe.kdeZoneBandwidth = bandwidth
        }
        if(plotFrame.isCurrentView){plotBackgroundLoader.startLoading()}
    }

    function switchToRaw() {
        menubar.selectMenu("RAW")
        menubar.clicked("RAW")
    }
    function switchToSTD() {
        menubar.selectMenu("STD")
        menubar.clicked("STD")
    }
    function switchToExceed() {
        menubar.selectMenu("EXD")
        menubar.clicked("EXD")
    }
    function switchToKDE() {
        menubar.selectMenu("KDE")
        menubar.clicked("KDE")
    }

    MMenuBar {
        id: menubar
        z: 1
        anchors{
            bottom: parent.bottom
            horizontalCenter: parent.horizontalCenter

            topMargin: 10
        }

        onClicked: (element) => {updateView(element)} 
    }

    Timer {
        id: plotBackgroundLoader
        interval: 3500
        repeat: true
        running: false
        triggeredOnStart: false
        property var allLoader: [occurrenceLoader, rawPlotLoader, filteredPlotLoader, intervallPlotLoader, stdPlotLoader, exceedPlotLoader, kdeExceedPlotLoader]
        property int counter: 0
        onTriggered: {
            console.info(Constants.PROGRESS_BAR, Constants.ID_PLOT, `Loading All Plots [${counter}/${allLoader.length}]`)
            while(counter < allLoader.length - 1 && allLoader[counter].active) {counter++}
            allLoader[counter++].backgroundLoading = true
            if(counter >= allLoader.length) {
                stopLoading()
            }
        }
        function startLoading() {
            counter = 0
            resetAll()
            start()
        }
        function stopLoading(reset = false) {
            stop()
            if (reset){resetAll()}
            console.info(Constants.PROGRESS_BAR, Constants.ID_PLOT, Constants.END_PROGRESS_BAR)
        }
        function resetAll() {
            console.log("resetting all background loading")
            for (let i = 0; i < allLoader.length; i++) {
                allLoader[i].backgroundLoading = false
            }
        }
    }

    onIsCurrentViewChanged: {
        if(isCurrentView){plotBackgroundLoader.startLoading()}
        else{plotBackgroundLoader.stopLoading(true)}
    }

    SwipeView {
        id: plotSwipe
        property var currentAddress: ""
        property string mode: ""
        property double kdeZoneLatitude: 0
        property double kdeZoneLongitude: 0
        property double kdeZoneBandwidth: 0

        anchors.fill: parent
        interactive: false

        Loader {
            id: occurrenceLoader
            property bool backgroundLoading: false
            active: backgroundLoading || (plotFrame.isCurrentView && (SwipeView.isCurrentItem || SwipeView.isPreviousItem))
            visible: status == Loader.Ready
            asynchronous: true
            sourceComponent: Component {
                MOccurrencePlot {
                    title: "Occurence Plot"
                    pointList: __mode_s.occurrenceSeries
                    titleFont: Constants.FONT_MEDIUM
                    titleColor: Constants.FONT_COLOR
                    theme: ChartView.ChartThemeBlueIcy
                }
            }
        }

        Loader {
            id: rawPlotLoader
            readonly property var addressData: __mode_s.addressRawSeries
            property bool backgroundLoading: false
            active: plotSwipe.currentAddress && (backgroundLoading || (plotSwipe.currentAddress == addressData["address"] && (plotSwipe.mode == Constants.LOCATION ||( plotFrame.isCurrentView && (SwipeView.isPreviousItem  ||  SwipeView.isCurrentItem || SwipeView.isNextItem)))))
            visible: true
            asynchronous: true
            sourceComponent: Component {
                id: rawPlotComponent
                MRawPlot {
                    id: rawPlot
                    title: "Bar & Ivv for Address " + addressData["address"]
                    bar: addressData["bar"]
                    ivv: addressData["ivv"]
                    time: addressData["time"]
                    address: addressData["address"]
                    identification: addressData["identification"]
                    titleFont: Constants.FONT_MEDIUM
                    titleColor: Constants.FONT_COLOR
                    theme: ChartView.ChartThemeBlueIcy
                }
            }
        }

        Loader {
            id: filteredPlotLoader
            readonly property var addressData: __mode_s.addressFilteredSeries
            property bool backgroundLoading: false
            active: plotSwipe.currentAddress && (backgroundLoading || (plotSwipe.currentAddress == addressData["address"] && (plotFrame.isCurrentView && (SwipeView.isPreviousItem  || SwipeView.isCurrentItem || SwipeView.isNextItem))))
            visible: status == Loader.Ready
            asynchronous: true
            sourceComponent: Component {
                Column {
                    id: filteredColumn
                    property alias repeater: nestedRepeater
                    Repeater {
                        id: nestedRepeater
                        model: addressData["points"]
                        property string address: addressData["address"]
                        property string identification: addressData["identification"]
                        delegate: MFilteredPlot {
                            id: filteredPlot
                            width: filteredColumn.width
                            height: filteredColumn.height / 2
                            title: "Filtered Bar & Ivv for Address " + nestedRepeater.address
                            dataSet: modelData["dataSet"]
                            raw: modelData["raw"]
                            filtered: modelData["filtered"]
                            time: modelData["time"]
                            address: nestedRepeater.address
                            identification: nestedRepeater.identification

                            titleFont: Constants.FONT_MEDIUM
                            titleColor: Constants.FONT_COLOR
                            theme: ChartView.ChartThemeBlueIcy
                        }
                    }
                }
            }
        }

        Loader {
            id: intervallPlotLoader
            readonly property var addressData: __mode_s.addressIntervalSeries
            property bool backgroundLoading: false
            active: plotSwipe.currentAddress && (backgroundLoading || (plotSwipe.currentAddress == addressData["address"] && (plotFrame.isCurrentView && (SwipeView.isPreviousItem  || SwipeView.isCurrentItem || SwipeView.isNextItem))))
            visible: status == Loader.Ready
            asynchronous: true
            sourceComponent: Component {
                MIntervalPlot {
                    id: intervalPlot
                    title: "Sliding Intervall for Address " + addressData["address"]
                    points: addressData["points"]
                    windows: addressData["windows"]
                    address: addressData["address"]
                    identification: addressData["identification"]

                    titleFont: Constants.FONT_MEDIUM
                    titleColor: Constants.FONT_COLOR
                    theme: ChartView.ChartThemeBlueIcy
                }
            }
        }

        Loader {
            id: stdPlotLoader
            readonly property var addressData: __mode_s.addressStdSeries
            property bool backgroundLoading: false
            active: plotSwipe.currentAddress && (backgroundLoading || (plotSwipe.currentAddress == addressData["address"] && (plotSwipe.mode == Constants.TURBULENCE || (plotFrame.isCurrentView  && (SwipeView.isPreviousItem  ||  SwipeView.isCurrentItem || SwipeView.isNextItem)))))
            visible: true
            asynchronous: true
            sourceComponent: Component {
                Row {
                    id: stdRows
                    property alias repeater: stdNestedRepeater
                    Repeater {
                        id: stdNestedRepeater
                        model: addressData["points"]
                        property string address: addressData["address"]
                        property string identification: addressData["identification"]
                        delegate: MSTDPlot {
                            id: stdPlot
                            width: stdRows.width / 2
                            height: stdRows.height 
                            address: stdNestedRepeater.address
                            identification: stdNestedRepeater.identification
                            std: modelData["dataSet"] == "STD"
                            title: {
                                let root = "Std Bar & Ivv for Address " + stdNestedRepeater.address
                                if (!stdPlot.std) {
                                    return "Diff " + root
                                }
                                return root
                            }
                            bar: {
                                if (stdPlot.std) {return modelData["bar"]}
                                else {return []}
                            }
                            ivv: {
                                if (stdPlot.std) {return modelData["ivv"]}
                                else {return []}
                            }
                            diff: {
                                if (!stdPlot.std) {return modelData["diff"]}
                                else {return []}
                            }
                            threshold: {
                                if (!stdPlot.std) {return modelData["threshold"]}
                                else {return -69}
                            }
                            windows: modelData["windows"]

                            titleFont: Constants.FONT_MEDIUM
                            titleColor: Constants.FONT_COLOR
                            theme: ChartView.ChartThemeBlueIcy
                        }
                    }
                }
            }
        }

        Loader {
            id: exceedPlotLoader
            readonly property var addressData: __mode_s.addressExceedSeries
            property bool backgroundLoading: false
            active: plotSwipe.currentAddress && (backgroundLoading || (plotSwipe.currentAddress == addressData["address"] && (plotSwipe.mode == Constants.TURBULENCE || (plotFrame.isCurrentView  && (SwipeView.isPreviousItem  ||  SwipeView.isCurrentItem || SwipeView.isNextItem)))))
            visible: true
            asynchronous: true
            sourceComponent: Component {
                MExceedPlot {
                    id: exceedPlot
                    title: "Threshold exceeds Distribution for Address " + addressData["address"]
                    address: addressData["address"]
                    identification: addressData["identification"]
                    distribution: addressData["distribution"]
                    smoothed: addressData["smoothed"]
                    
                    distChart.titleFont: Constants.FONT_MEDIUM
                    distChart.titleColor: Constants.FONT_COLOR
                    distChart.theme: ChartView.ChartThemeBlueIcy
                    
                    smoothChart.titleFont: Constants.FONT_MEDIUM
                    smoothChart.titleColor: Constants.FONT_COLOR
                    smoothChart.theme: ChartView.ChartThemeBlueIcy
                }
            }
        }

        Loader {
            id: kdeExceedPlotLoader
            readonly property var zoneData: __mode_s.zoneKdeExceedSeries
            property bool backgroundLoading: false
            active: plotSwipe.kdeZoneBandwidth && (backgroundLoading || ((plotSwipe.kdeZoneLatitude == zoneData["latitude"] && plotSwipe.kdeZoneLongitude == zoneData["longitude"]) || (plotFrame.isCurrentView  && SwipeView.isCurrentItem)))
            visible: true
            asynchronous: true
            sourceComponent: Component {
                MExceedKDEZonePlot {
                    id: kdeExceedPlot
                    title: `KDE for Zone ${zoneData.latitude.toFixed(2)}N, ${zoneData.longitude.toFixed(2)}E, Offset: +/-${(plotSwipe.kdeZoneBandwidth / 2).toFixed(2)}`
                    latitude: zoneData["latitude"]
                    longitude: zoneData["longitude"]
                    exceedsPerAddress: zoneData["exceedsPerAddress"]
                    kde: zoneData["kde"]

                    titleFont: Constants.FONT_MEDIUM
                    titleColor: Constants.FONT_COLOR
                    theme: ChartView.ChartThemeBlueIcy
                }
            }
        }

        Connections {
            target: kdeExceedPlotLoader.item

            function onAddressClicked(address) {
                plotFrame.preparePlotsForAddress(address, Constants.TURBULENCE)
                plotFrame.switchToExceed()
            }

            function onAddressHovered(address, identification, start, end , r, g, b) {
                kdeAddressInfoShower.leColor = Qt.rgba(r,g,b,1)
                kdeAddressInfoShower.startLoadingTimerFor(address, identification, start , end)
            }

            function onResetHovered(){
                kdeAddressInfoShower.stop()
            }
        }

        Timer {
            id: kdeAddressInfoShower
            interval: 1500
            repeat: false
            triggeredOnStart: false
            property string address: ""
            property string identification: ""
            property string flightStart: ""
            property string fligthEnd: ""
            property color leColor: "pink"
            onTriggered: {
                mapElementInfo.identification = identification
                mapElementInfo.address = address
                mapElementInfo.flightColor = leColor
                mapElementInfo.displayText = "Selected Area"
                mapElementInfo.datapoints = `\nFrom ${flightStart} to ${fligthEnd} [min]`
                mapElementInfo.turbulentFlight = true
                mapElementInfo.buttonShowGraph = true
                mapElementInfo.mode = Constants.TURBULENCE
                mapElementInfo.open()
                plotFrame.preparePlotsForAddress(address, Constants.TURBULENCE)
            }

            function startLoadingTimerFor(address, identification, start , end) {
                kdeAddressInfoShower.address = address
                kdeAddressInfoShower.identification = identification
                kdeAddressInfoShower.flightStart = start
                kdeAddressInfoShower.fligthEnd = end
                kdeAddressInfoShower.start()
            }
        }
    }
}
