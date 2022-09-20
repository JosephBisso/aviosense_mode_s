import QtQml 2.15
import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import QtQml.Models 2.15
import "qrc:/scripts/constants.js" as Constants

Rectangle {
    id: rootMenuBar
    property int buttonWidth: 55
    width: buttonLayout.implicitWidth + 50
    height: 70
    radius: 50
    color: Qt.rgba(255, 255, 255, 0.2)
    opacity: 0.4
    layer.enabled: true
    layer.effect: DropShadow {
        color: "black"
        horizontalOffset: 3
        verticalOffset: 3
        radius: 3
    }
    property ListModel models: ListModel{
        ListElement {
            name: "OCC"
            fullName: "Occurrence"
        }
        ListElement {
            name: "RAW"
            fullName: "Raw bar & ivv"
        }
        ListElement {
            name: "FIL"
            fullName: "Filtered bar & ivv"
        }
        ListElement {
            name: "INT"
            fullName: "Sliding Intervall"
        }
        ListElement {
            name: "STD"
            fullName: "Standard deviation"
        }
        ListElement {
            name: "EXD"
            fullName: "Exceed Distribution"
        }
        ListElement {
            name: "KDE"
            fullName: "Distribution per Zone"
        }
    }

    signal clicked(string element)

    Component.onCompleted: selectMenu(models.get(0).name)

    function selectMenu(menu) {
        for (let i = 0; i < menuRepeater.count; i++) {
            if (menuRepeater.itemAt(i).menuName == menu)  {
                menuRepeater.itemAt(i).mChecked = true
            } else {
                menuRepeater.itemAt(i).mChecked = false
            }
        }
    }

    Behavior on opacity {NumberAnimation {duration: 150}}


    Timer {
        id: fadeTimer
        interval: 500

        onTriggered: {
            rootMenuBar.opacity = 0.4
        }
    }

    RowLayout {
        id: buttonLayout
        spacing: 20
        anchors.centerIn: parent
        Repeater {
            id: menuRepeater
            model: models
            delegate: MButton {
                id: buttonDelegate
                property string menuName: name
                width:buttonWidth
                height:width
                radius: width/2
                mText: name 
                mToolTipText: fullName
                mFont: Constants.FONT_SMALL
                mDefaultColor: Constants.GLASSY_BLACK_BACKGROUND
                mHoverColor: Constants.FOREGROUND_COLOR
                mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
                mTextColor: "white"
                opacity: rootMenuBar.opacity
                mCheckable: true
                mManualUncheckable: false
                onClicked: {
                    rootMenuBar.selectMenu(menuName)
                    rootMenuBar.clicked(name)
                }

                onMouseEnter: {
                    rootMenuBar.opacity = 1
                    fadeTimer.stop()
                }

                onMouseOut: {
                    fadeTimer.start()
                }
            }
        }
    }
}
