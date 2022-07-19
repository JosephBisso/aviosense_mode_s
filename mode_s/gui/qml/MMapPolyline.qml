import QtLocation 5.15
import QtQuick 2.15

MapPolyline {
    id: polyLine
    property var address: "None"
    property var identification: "None"
    property color lineColor: "red"
    property real defaultOpacity: 0.4
    property real defaultLineWidth: 5
    line.width: defaultLineWidth
    line.color: lineColor
    opacity: defaultOpacity
    path:[]

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.CrossCursor
        onEntered: show()
        onExited: reset()
        onClicked: {
            console.log("Clicked:", address, "::", identification)
        }
    }

    function reset() {
        polyLine.opacity = defaultOpacity
        polyLine.line.width = defaultLineWidth
    }

    function show() {
        polyLine.opacity = 1
        polyLine.line.width = 7
    }
}
