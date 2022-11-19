import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml.Models 2.15
import "qrc:/scripts/constants.js" as Constants
import "qrc:/scripts/util.js" as Util

Popup {
    id: rootPopup

    property string identification: "IDENTIFICATION"
    property string address: "address"
    property color flightColor: "blue"
    property var datapoints: -69
    property string displayText: "Data points"
    property bool turbulentFlight: false
    property bool buttonShowGraph: true
    property string mode: Constants.LOCATION

    property var control: parent
    property var mHeight: {Math.max((4/15) * parent.height, 275)}

    x: 150
    y: 20
    width: mHeight

    clip: true
    closePolicy: Popup.CloseOnPressOutside

    background: Rectangle {
        color: Util.transparentBy(rootPopup.flightColor, 0.2)
        radius: 10
        border {
            width: Constants.BORDER_WIDTH
            color: rootPopup.flightColor
        }
    }

    onOpened: {console.log("Opened flight info: ", identification, address, flightColor)}

    enter: Transition {
        ParallelAnimation {
            NumberAnimation {
                property: "opacity"
                from: 0
                to: 1.0
                duration: 100
            }
            NumberAnimation {
                property: "height"
                from: 0
                to: mHeight
                duration: 100
            }
        }
    }

    exit: Transition {
        ParallelAnimation {
            NumberAnimation {
                property: "opacity"
                to: 0
                duration: 75
            }
            NumberAnimation {
                property: "height"
                to: 0
                duration: 75
            }
        }
    }

    contentItem: ColumnLayout {
        id: contentColumn
        height: parent.height
        width: parent.width
        anchors {
            fill: parent
            margins: 10
        }
        spacing: 10

        Label {
            text: rootPopup.identification
            font: Constants.FONT_BIG
            color: Constants.FONT_COLOR
            Layout.alignment: Qt.AlignLeft
        }
        Label {
            text: rootPopup.address
            font: Constants.FONT_MEDIUM_NOT_BOLD
            color: Constants.FONT_COLOR
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            Layout.topMargin: -10

        }

        Label {
            text: "TURBULENT FLIGHT"
            font: Constants.FONT_VERY_SMALL
            visible: rootPopup.turbulentFlight
            color: Qt.darker("red", 1.5)
            Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
            Layout.bottomMargin: -10
        }
        Label {
            text: `${rootPopup.displayText}: ${rootPopup.datapoints}`
            font: Constants.FONT_VERY_SMALL
            color: Constants.FONT_COLOR
            Layout.alignment: Qt.AlignLeft
        }
    
        MIMGButton {
            id: buttonDelegate
            z:1

            Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
            Layout.bottomMargin: 10

            width:50
            img_src: rootPopup.buttonShowGraph ? "qrc:/img/noise.png" : "qrc:/img/gaussian-function.png"
            mFont: Constants.FONT_SMALL
            mDefaultColor: Constants.GLASSY_BLACK_BACKGROUND
            mHoverColor: Constants.FOREGROUND_COLOR
            mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
            mTextColor: "white"
            opacity: 1
            mToolTipText: `Flight Data of ${rootPopup.identification}` 

            onClicked: {
                verticalMenuBar.selectMenu("noise")
                verticalMenuBar.clicked("noise")
                if (rootPopup.buttonShowGraph) {
                    if (rootPopup.mode == Constants.LOCATION) {
                        plotView.switchToRaw()
                    } else {
                        plotView.switchToSTD()
                    }
                } else {
                    plotView.switchToKDE()
                }
                rootPopup.close()
            }
        }

    }

}
