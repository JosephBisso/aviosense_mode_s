import QtQml 2.15
import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import "qrc:/scripts/Constants.js" as Constants

Rectangle {
    id: rootMenuBar
    property int buttonWidth: 50
    property var models: ["world", "noise"]
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

    signal clicked(string element)

    Component.onCompleted: selectMenu(models[0])

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
            model: rootMenuBar.models
            MIMGButton {
                id: buttonDelegate
                property string menuName: modelData
                width:buttonWidth
                img_src: `qrc:/img/${modelData}.png`
                mFont: Constants.FONT_SMALL
                mDefaultColor: Qt.rgba(Constants.FONT_COLOR.r, Constants.FONT_COLOR.g, Constants.FONT_COLOR.b, 0.5)
                mHoverColor: Constants.FOREGROUND_COLOR
                mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
                mTextColor: "white"
                opacity: rootMenuBar.opacity
                mCheckable: true
                mManualUncheckable: false

                onClicked: {
                    rootMenuBar.selectMenu(modelData)
                    rootMenuBar.clicked(modelData)
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
