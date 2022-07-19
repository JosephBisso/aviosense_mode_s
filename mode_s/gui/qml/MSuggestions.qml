import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml.Models 2.15

import "qrc:/scripts/Constants.js" as Constants

Popup {
    id: rootPopup
    property var control: parent
    property ListModel suggestions: ListModel{}
    property var mHeight: 300

    y: control.height + 20
    width: control.width
    height: 0
    closePolicy: Popup.CloseOnPressOutside
    opacity: 0

    background: Rectangle {
        property color leColor: "white"
        color: Constants.transparentBy(leColor, 0.5)
        radius: 10
        border {
            width: Constants.BORDER_WIDTH
            color: Constants.BACKGROUND_COLOR2
        }
    }

    enter: Transition {
        ParallelAnimation {
            NumberAnimation {
                property: "opacity"
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

    signal itemSelected(int itemName)

    contentItem: Column {
        id: contentColumn
        height: implicitHeight
        width: parent.width
        anchors {
            fill: parent
            margins: 10
        }
        spacing: 10

        ScrollView {
            id: scrollView
            implicitHeight: parent.height
            width: parent.width

            clip: true
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            ListView {
                id: itemList
                width: parent.width
                implicitHeight: contentHeight
                model: rootPopup.suggestions
                clip: true
                spacing: 25
                
                delegate: Rectangle {
                    id: item
                    property color leColor: Constants.FOREGROUND_COLOR
                    color: "transparent"
                    radius: 10
                    width: itemList.width
                    height: 75
                    MouseArea {
                        anchors.fill: parent
                        z: 1
                        cursorShape: Qt.PointingHandCursor
                        hoverEnabled: true
                        onContainsMouseChanged: {
                            if (containsMouse) {item.color = Constants.transparentBy(leColor, 0.5)}
                            else {item.color = "transparent"}
                        }
                        onClicked: (event) => {
                            if (event.button === Qt.LeftButton) {
                                rootPopup.itemSelected(Number(address))
                            }
                        }
                    }
                    ColumnLayout {
                        anchors.fill: parent
                        Label {
                            text: identification
                            font: Constants.FONT_SMALL
                            color: Constants.FONT_COLOR
                            Layout.alignment: Qt.AlignLeft 
                        }
                        Label {
                            text: address
                            font: Constants.FONT_VERY_SMALL
                            color: Constants.FONT_COLOR
                            Layout.alignment: Qt.AlignRight
                        }
                    }
                }
                ScrollIndicator.vertical: ScrollIndicator { }
            }

        }
    }


}
