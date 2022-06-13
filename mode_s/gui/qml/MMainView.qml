import QtQuick
import QtCharts
import QtQuick.Layouts
import QtQuick.Controls
import "qrc:/scripts/Constants.js" as Constants

SwipeView {
    id: rootSwipe
    currentIndex: 1
    property int currentAddressIndex: 0

    function updateView(name) {
        switch(name) {
            case "RAW":
                currentIndex = 0
                break;
            case "OCC":
                currentIndex = 1
                break;
            case "FIL":
                currentIndex = 2
                break;
            case "INT":
                currentIndex = 3
                break;
            case "STD":
                currentIndex = 4
                break;
            case "LOC":
                currentIndex = 5
                break;
        }
    }   

    SwipeView {
        id: rawPlots
        currentIndex: currentAddressIndex
        orientation: Qt.Vertical
        
        Connections {
            target: __mode_s

            function onPlotRawReady(pointList) {
                rawPlotRepeater.model = pointList
            }
        }
        Repeater {
            id: rawPlotRepeater
            delegate: MRawPlot {
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

    MOccurrencePlot {
        title: "Occurence Plot"
        titleFont: Constants.FONT_MEDIUM
        titleColor: Constants.FONT_COLOR
        theme: ChartView.ChartThemeBlueIcy
    }

    SwipeView {
        id: filteredPlots
        currentIndex: currentAddressIndex
        orientation: Qt.Vertical
        
        Connections {
            target: __mode_s

            function onPlotFilteredReady(pointList) {
                filteredPlotRepeater.model = pointList
            }
        }
        Repeater {
            id: filteredPlotRepeater
            property string address: ""
            delegate: Column {
                id: filteredColumn
                Repeater {
                    id: nestedRepeater
                    model: modelData["points"]
                    property string address
                    delegate: MFilteredPlot {
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

    SwipeView {
        id: intervallPlots
        currentIndex: currentAddressIndex
        orientation: Qt.Vertical
        
        Connections {
            target: __mode_s

            function onPlotIntervalReady(pointList) {
                intervalPlotRepeater.model = pointList
            }
        }
        Repeater {
            id: intervalPlotRepeater
            delegate: MIntervalPlot {
                title: "Sliding Intervall for Address " + modelData["address"]
                points: modelData["points"]
                windows: modelData["windows"]

                titleFont: Constants.FONT_MEDIUM
                titleColor: Constants.FONT_COLOR
                theme: ChartView.ChartThemeBlueIcy
            }
        }
    }

    SwipeView {
        id: stdPlots
        currentIndex: currentAddressIndex
        orientation: Qt.Vertical
        
        Connections {
            target: __mode_s

            function onPlotStdReady(pointList) {
                stdPlotRepeater.model = pointList
            }
        }
        Repeater {
            id: stdPlotRepeater
            delegate: Row {
                id: stdRows
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
