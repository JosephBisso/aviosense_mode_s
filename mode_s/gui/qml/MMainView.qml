import QtQuick.Layouts
import QtQuick

StackLayout {
    id: rootStack
    currentIndex: 1

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

    Repeater {
        id: allPlots
        model: ["Raw", "Occurrence", "Filtered", "Interval", "Std", "Location"]
        MPlot {
            title: modelData
        }
    }
}
