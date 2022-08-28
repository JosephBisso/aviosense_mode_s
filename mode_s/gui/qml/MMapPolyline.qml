import QtLocation 5.15
import QtQuick 2.15

MapPolyline {
    id: polyLine
    property var address: "None"
    property var identification: "None"
    property color lineColor: "red"
    property real defaultOpacity: 0.5
    property real defaultLineWidth: 5
    property bool selected: false
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
            polyLine.parent.addressClicked(polyLine, address)
        }
    }

    function reset() {
        selected = false
        polyLine.opacity = defaultOpacity
        polyLine.line.width = defaultLineWidth
    }

    function show() {
        selected = true
        polyLine.opacity = 1
        polyLine.line.width = 8
    }
}
