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
        anchors.fill: parent
        MOccurrencePlot {
            title: "Occurence Plot"
            titleFont: Constants.FONT_MEDIUM
            titleColor: Constants.FONT_COLOR
            theme: ChartView.ChartThemeBlueIcy
        }

        SwipeView {
            id: rawPlots
            property bool isCurrentPlot: plotFrame.isCurrentView && SwipeView.isCurrentItem
            Connections {
                target: __mode_s

                function onPlotRawReady(pointList) {
                    rawPlotRepeater.model = pointList
                }
            }
            Repeater {
                id: rawPlotRepeater
                delegate: Loader {
                    id: rawPlotLoader
                    active: rawPlots.isCurrentPlot && SwipeView.isCurrentItem
                    asynchronous: true
                    sourceComponent: Component {
                        id: rawPlotComponent
                        MRawPlot {
                            id: rawPlot
                            title: "Bar & Ivv for Address " + modelData["address"]
                            bar: modelData["bar"]
                            ivv: modelData["ivv"]
                            time: modelData["time"]

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
            property bool isCurrentPlot: plotFrame.isCurrentView && SwipeView.isCurrentItem
            Connections {
                target: __mode_s

                function onPlotFilteredReady(pointList) {
                    filteredPlotRepeater.model = pointList
                }
            }
            Repeater {
                id: filteredPlotRepeater
                property string address: ""
                delegate: Loader {
                    id: filteredPlotLoader
                    active: filteredPlots.isCurrentPlot && SwipeView.isCurrentItem
                    asynchronous: true
                    sourceComponent: Component {
                        Column {
                            id: filteredColumn
                            property alias repeater: nestedRepeater
                            Repeater {
                                id: nestedRepeater
                                model: modelData["points"]
                                property string address
                                delegate: MFilteredPlot {
                                    id: filteredPlot
                                    width: filteredColumn.width
                                    height: filteredColumn.height / 2
                                    title: "Filtered Bar & Ivv for Address " + nestedRepeater.address
                                    dataSet: modelData["dataSet"]
                                    raw: modelData["raw"]
                                    filtered: modelData["filtered"]
                                    time: modelData["time"]

                                    titleFont: Constants.FONT_MEDIUM
                                    titleColor: Constants.FONT_COLOR
                                    theme: ChartView.ChartThemeBlueIcy
                                }

                                Component.onCompleted: nestedRepeater.address = Qt.binding(()=>{return modelData["address"]})
                            }
                        }
                    }
                }
            }
        }

        SwipeView {
            id: intervallPlots
            property bool isCurrentPlot: plotFrame.isCurrentView && SwipeView.isCurrentItem
            Connections {
                target: __mode_s

                function onPlotIntervalReady(pointList) {
                    intervalPlotRepeater.model = pointList
                }
            }
            Repeater {
                id: intervalPlotRepeater
                delegate: Loader {
                    id: intervallPlotLoader
                    active: intervallPlots.isCurrentPlot && SwipeView.isCurrentItem
                    asynchronous: true
                    sourceComponent: Component {
                        MIntervalPlot {
                            id: intervalPlot
                            title: "Sliding Intervall for Address " + modelData["address"]
                            points: modelData["points"]
                            windows: modelData["windows"]

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
            property bool isCurrentPlot: plotFrame.isCurrentView && SwipeView.isCurrentItem
            Connections {
                target: __mode_s

                function onPlotStdReady(pointList) {
                    stdPlotRepeater.model = pointList
                }
            }
            Repeater {
                id: stdPlotRepeater
                delegate: Loader {
                    id: stdPlotLoader
                    active: stdPlots.isCurrentPlot && SwipeView.isCurrentItem
                    asynchronous: true
                    sourceComponent: Component {
                        Row {
                            id: stdRows
                            property alias repeater: stdNestedRepeater
                            Repeater {
                                id: stdNestedRepeater
                                model: modelData["points"]
                                property string address: modelData["address"]
                                delegate: MSTDPlot {
                                    id: stdPlot
                                    width: stdRows.width / 2
                                    height: stdRows.height 

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
