/*!
    \qmlclass CustomBusyIndicator
    \brief The busy indicator shown every time there is an ongoing operation

    \sa MainView, File, AppeareanceSettings

*/

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQml
import Qt5Compat.GraphicalEffects
import "qrc:/scripts/Constants.js" as Constants

Popup {
    id: rootPane

    property string mTitle: "Working..."
    property color mBorderColor: "white"
    x: rootWindow.width / 2 - width/2
    y: rootWindow.height / 2 - height/2
    width: 3/4 * rootWindow.width
    height: 3/4 * rootWindow.height
    scale: 0.2
    opacity: 0.2
    dim: true
    modal: true
    closePolicy: Popup.NoAutoClose

    enter: Transition {
        ParallelAnimation {
            NumberAnimation {
                property: "opacity"
                to: 1.0
                duration: 150
            }
            NumberAnimation {
                property: "scale"
                to: 1
                duration: 150
            }
        }
    }

    exit: Transition {
        ParallelAnimation {
            NumberAnimation {
                property: "opacity"
                to: 0.2
                duration: 75
            }
            NumberAnimation {
                property: "scale"
                to: 0.2
                duration: 75
            }
        }
    }


    background: Rectangle {
        anchors.fill: parent
        radius: 10
        color: Constants.BACKGROUND_COLOR2
        border {
            width: 1
            color: rootPane.mBorderColor
        }
    }

    Connections {
        target: __mode_s

        function onLogged(log)  {
            busyTextArea.text += log    
        }

        function onComputingStarted() {
            busyIndicator.visible = true
            indicatorTitle.text = mTitle
            rootPane.mBorderColor = "white"
            rootPane.open()
        }

        function onComputingFinished() {
            busyIndicator.visible = false
            indicatorTitle.text = "Done"
            rootPane.mBorderColor = "lime"
            closingTimer.start()
        }
    }

    Timer {
        id: closingTimer
        interval: 2500
        onTriggered: {
            rootPane.close()
        }
    }

    ColumnLayout {
        id: contentLayout
        anchors {
            fill: parent
            margins: 20
        }

        spacing: 20

        Label {
            id: indicatorTitle
            Layout.alignment: Qt.AlignHCenter | Qt.AlignTop
            text: mTitle
            font: Constants.FONT_MEDIUM
            color: Constants.FONT_COLOR
        }

        BusyIndicator {
            id: busyIndicator
            Layout.alignment: Qt.AlignHCenter
            running: true

            ColorOverlay {
                id: fileOverlay
                source: busyIndicator
                anchors.fill: busyIndicator
                color: Constants.FONT_COLOR
            }

        }

        ScrollView {
            id: view
            Layout.fillWidth: true
            Layout.fillHeight: true
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            Flickable {
                id: flick
                width: parent.width
                height: parent.height
                flickableDirection: Flickable.VerticalFlick
                contentHeight: busyTextArea.implicitHeight
                clip: true
                
                onContentHeightChanged: Qt.callLater(() => contentY = contentHeight - height)

                TextArea.flickable: TextArea {
                    id: busyTextArea
                    readOnly: true
                    textFormat: TextEdit.AutoText
                    text: "<p style='color:Orange;'><b>Full log in: '%MODE-S_INSTALL_PATH%/mode_s.log' </b></p>"
                    color: "white"
                    font: Constants.FONT_SMALL
                    selectByMouse: true
                    persistentSelection: true
                    cursorVisible: true
                    wrapMode: TextEdit.Wrap

                    background: Rectangle{
                        anchors.fill: parent
                        color: "black"
                        radius: 10
                    }
                }       
            }
        }

    }

}