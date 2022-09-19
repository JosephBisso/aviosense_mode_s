import QtQuick 2.15
import QtLocation 5.15
import QtPositioning 5.15
import Qt.labs.location 1.0

MapRectangle {
    id: kdeZone
    property double kde_e: 1
    property double kde_normed: 1
    property double centerLatitude : 0
    property double centerLongitude : 0
    property double bw : 0.5
    property int zoneID : 0

    property bool hovered : rectangleMouseArea.containsMouse 

    color: {
        if (kde_normed < 0.5) {return "orangered"}
        else if (0.5 <= kde_normed && kde_normed < 0.75) {return "red"}
        else {return "darkred"}
    }

    opacity: {
        if (kde_normed < 0.5) {return 0.1}
        else if (0.5 <= kde_normed && kde_normed < 0.75) {return 0.15}
        else {return 0.2}
    }

    border {
        color: kdeZone.hovered ? "skyblue" : "transparent"
        width: 8
    }

    topLeft: QtPositioning.coordinate(centerLatitude - bw/2, centerLongitude - bw/2)
    bottomRight: QtPositioning.coordinate(centerLatitude + bw/2, centerLongitude + bw/2)

    MouseArea {
        id: rectangleMouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: {
            console.log("Clicked kde_e Zone ", centerLatitude, "°N", centerLongitude, "°W :: ", kde_e, " >> ", kde_normed)
            kdeZone.parent.zoneKDEClicked(kdeZone)
        }
    }

}
