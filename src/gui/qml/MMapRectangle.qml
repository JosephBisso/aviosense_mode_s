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
    property double tlLon: 0
    property double tlLat: 0
    property double brLon: 0
    property double brLat: 0
    property double bw : 0.5
    property int zoneID : 0
    property int numFligths : 0
    property double fieldwidth : 0

    property bool hovered : rectangleMouseArea.containsMouse 

    color: {
        if (kde_normed < 0.5) {return "orangered"}
        else if (0.5 <= kde_normed && kde_normed < 0.75) {return "red"}
        else {return "darkred"}
    }

    opacity: {
        if (kde_normed < 0.5) {return 0.09}
        else if (0.5 <= kde_normed && kde_normed < 0.75) {return 0.12}
        else {return 0.2}
    }

    border {
        color: kdeZone.hovered ? "skyblue" : "transparent"
        width: 8
    }

    topLeft: QtPositioning.coordinate(tlLat, tlLon)
    bottomRight: QtPositioning.coordinate(brLat, brLon)

    MouseArea {
        id: rectangleMouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: {
            console.log("Clicked kde_e Zone ", centerLatitude, "N", centerLongitude, "W  <::> ", "num of Fligths:", numFligths, "zoneID", zoneID)
            kdeZone.parent.zoneKDEClicked(kdeZone)
        }
    }

}
