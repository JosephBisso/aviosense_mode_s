import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import QtQml 2.15
import "qrc:/scripts/Constants.js" as Constants

Frame {
    id: plotFrame
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
        }
    }   

    function preparePlotsForAddress(address) {
        plotSwipe.currentAddress = address
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

    SwipeView {
        id: plotSwipe
        property var currentAddress: ""
        anchors.fill: parent
        MOccurrencePlot {
            title: "Occurence Plot"
            titleFont: Constants.FONT_MEDIUM
            titleColor: Constants.FONT_COLOR
            theme: ChartView.ChartThemeBlueIcy
        }

        SwipeView {
            id: rawPlots
            interactive: false

            function showCurrentAddress(indexOfLoadedItem) {
                setCurrentIndex(indexOfLoadedItem)
            }

            Repeater {
                id: rawPlotRepeater
                model: __mode_s.rawSeries
                delegate: Loader {
                    id: rawPlotLoader
                    active: plotSwipe.currentAddress == modelData["address"] || (plotFrame.isCurrentView && SwipeView.isCurrentItem)
                    asynchronous: true
                    onLoaded: rawPlots.showCurrentAddress(SwipeView.index)

                    sourceComponent: Component {
                        id: rawPlotComponent
                        MRawPlot {
                            id: rawPlot
                            title: "Bar & Ivv for Address " + modelData["address"]
                            bar: modelData["bar"]
                            ivv: modelData["ivv"]
                            time: modelData["time"]
                            address: modelData["address"]
                            identification: modelData["identification"]
                            titleFont: Constants.FONT_MEDIUM
                            titleColor: Constants.FONT_COLOR
                            theme: ChartView.ChartThemeBlueIcy
                        }
                    }
                }
            }
        }

        SwipeView {
            id: filteredPlots

            function showCurrentAddress(indexOfLoadedItem) {
                setCurrentIndex(indexOfLoadedItem)
            }

            Repeater {
                id: filteredPlotRepeater
                model: __mode_s.filteredSeries

                delegate: Loader {
                    id: filteredPlotLoader
                    active: plotSwipe.currentAddress == modelData["address"] || (plotFrame.isCurrentView && SwipeView.isCurrentItem)
                    asynchronous: true
                    onLoaded: filteredPlots.showCurrentAddress(SwipeView.index)
                    sourceComponent: Component {
                        Column {
                            id: filteredColumn
                            property alias repeater: nestedRepeater
                            Repeater {
                                id: nestedRepeater
                                model: modelData["points"]
                                property string address: modelData["address"]
                                property string identification: modelData["identification"]
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
            }
        }

        SwipeView {
            id: intervallPlots

            function showCurrentAddress(indexOfLoadedItem) {
                setCurrentIndex(indexOfLoadedItem)
            }
            Repeater {
                id: intervalPlotRepeater
                model: __mode_s.intervalSeries

                delegate: Loader {
                    id: intervallPlotLoader
                    active: plotSwipe.currentAddress == modelData["address"] || (plotFrame.isCurrentView && SwipeView.isCurrentItem)
                    asynchronous: true
                    onLoaded: intervallPlots.showCurrentAddress(SwipeView.index)
                    sourceComponent: Component {
                        MIntervalPlot {
                            id: intervalPlot
                            title: "Sliding Intervall for Address " + modelData["address"]
                            points: modelData["points"]
                            windows: modelData["windows"]
                            address: modelData["address"]
                            identification: modelData["identification"]

                            titleFont: Constants.FONT_MEDIUM
                            titleColor: Constants.FONT_COLOR
                            theme: ChartView.ChartThemeBlueIcy
                        }
                    }
                }
            }
        }

        SwipeView {
            id: stdPlots

            function showCurrentAddress(indexOfLoadedItem) {
                setCurrentIndex(indexOfLoadedItem)
            }
            Repeater {
                id: stdPlotRepeater
                model: __mode_s.stdSeries
                delegate: Loader {
                    id: stdPlotLoader
                    active: plotSwipe.currentAddress == modelData["address"] || (plotFrame.isCurrentView && SwipeView.isCurrentItem)
                    asynchronous: true
                    onLoaded: stdPlots.showCurrentAddress(SwipeView.index)
                    sourceComponent: Component {
                        Row {
                            id: stdRows
                            property alias repeater: stdNestedRepeater
                            Repeater {
                                id: stdNestedRepeater
                                model: modelData["points"]
                                property string address: modelData["address"]
                                property string identification: modelData["identification"]
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
            }
        }
    }
}
