import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtQml 2.15
import "qrc:/scripts/Constants.js" as Constants

Frame {
    id: rootMainView
    anchors.fill: parent

    background: Rectangle {
        color: "transparent"
        border.color: "transparent"
        radius: 10
    }

    function updateView(name) {
        switch(name) {
            case "world":
                rootSwipe.currentIndex = 0
                break;
            case "noise":
                rootSwipe.currentIndex = 1
                break;
        }
    } 

    MVerticalMenuBar {
        id: verticalMenuBar
        z: 1
        anchors {
            top: parent.top
            right: parent.right

            margins: 20
        }

        onClicked: (element) => {rootMainView.updateView(element)}
    }

    MIMGButton {
        id: saveButton
        img_src:"qrc:/img/download.png"
        z: 1

        anchors {
            bottom: parent.bottom
            right: parent.right

            margins: 20
        }

    }

    SwipeView {
        id: rootSwipe
        orientation: Qt.Vertical
        anchors.fill: parent
        interactive: false

        MMap {
            id: mapView
            Connections {
                target: __mode_s

                function onPlotLocationReady(pointList) {
                    mapView.location = pointList
                    mapView.showLocation()
                }
            }
        }

        MPlots {
            id: plotView
            property bool isCurrentView: SwipeView.isCurrentItem

        }
    }
}
