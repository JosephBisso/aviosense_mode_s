import QtQml 2.15
import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import QtQml.Models 2.15
import "qrc:/scripts/Constants.js" as Constants

Rectangle {
    id: rootMenuBar
    property int buttonWidth: 50
    width: 70
    height: 150
    radius: width
    color: Qt.rgba(255, 255, 255, 0.2)
    opacity: 0.4
    layer.enabled: true
    layer.effect: DropShadow {
        color: "black"
        horizontalOffset: 3
        verticalOffset: 3
        radius: 3
    }
    property ListModel models: ListModel {
        ListElement {
            name: "world"
            fullName: "Map"
        }
        ListElement {
            name: "noise"
            fullName: "Data"
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

    ColumnLayout {
        spacing: 20
        anchors.centerIn: parent
        Repeater {
            id: menuRepeater
            model: models
            delegate: MIMGButton {
                id: buttonDelegate
                property string menuName: name
                width:buttonWidth
                img_src: `qrc:/img/${name}.png`
                mFont: Constants.FONT_SMALL
                mDefaultColor: Constants.GLASSY_BLACK_BACKGROUND
                mHoverColor: Constants.FOREGROUND_COLOR
                mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
                mTextColor: "white"
                opacity: rootMenuBar.opacity
                mCheckable: true
                mManualUncheckable: false
                mToolTipText: `${fullName}`

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
