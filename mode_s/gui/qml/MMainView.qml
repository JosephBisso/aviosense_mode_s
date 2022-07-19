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
        id: sideButton
        img_src: "qrc:/img/hamburger.png"
        z: 1
        anchors {
            top: parent.top
            left: parent.left

            margins: 20
        }
        mDefaultColor: Qt.rgba(0,0,0,0.8)
        mHoverColor: Constants.FOREGROUND_COLOR
        mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
        mToolTipText: "Menu"
        onClicked: {
            if (sideBar.opened) {sideBar.close();return}
            sideBar.open()
        }
    }
    
    MIMGButton {
        id: saveButton
        img_src:"qrc:/img/download.png"
        z: 1
        mToolTipText: "Export"

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
