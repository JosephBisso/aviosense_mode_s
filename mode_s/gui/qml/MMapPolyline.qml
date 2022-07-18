import QtLocation 5.15
import QtQuick 2.15

MapPolyline {
    property var address: "None"
    property color lineColor: "red"
    line.width: 5
    line.color: lineColor
    path:[]

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.CrossCursor
        onClicked: console.log("Clicked", address)
    }
}
