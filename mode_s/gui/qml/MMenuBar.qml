import QtQml
import QtQuick
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import "qrc:/scripts/Constants.js" as Constants

Rectangle {
    id: rootMenuBar
    width: 450
    height: 65
    radius: 50
    color: Qt.rgba(255, 255, 255, 0.2)
    opacity: 0.2
    property int buttonWidth: 45

    layer.enabled: true
    layer.effect: DropShadow {
        color: "black"
        horizontalOffset: 3
        verticalOffset: 3
        radius: 3
    }

    Behavior on opacity {NumberAnimation {duration: 150}}
    
    Timer {
        id: fadeTimer
        interval: 1000

        onTriggered: {
            rootMenuBar.opacity = 0.2
        }
    }

    RowLayout {
        spacing: 20
        anchors.centerIn: parent
        Repeater {
            model: ["RAW","OCC", "FIL", "INT", "STD", "LOC"]
            MButton {
                id: buttonDelegate
                width:buttonWidth
                height:width
                radius: width/2
                mText: modelData 
                mFont: Constants.FONT_SMALL
                mDefaultColor: Qt.rgba(Constants.FONT_COLOR.r, Constants.FONT_COLOR.g, Constants.FONT_COLOR.b, 0.5)
                mHoverColor: Constants.FOREGROUND_COLOR
                mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
                mTextColor: "white"
                opacity: rootMenuBar.opacity

                onClicked: {
                    indicator.visible = true
                    indicator.x = x + width -1.5/10 *width
                    mainView.updateView(modelData)
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

    Rectangle {
        id: indicator
        width: buttonWidth + 5
        height: 4
        radius: height
        color: Constants.ACCENT_COLOR1
        anchors.bottom: parent.bottom
        visible: false

        Behavior on x {NumberAnimation{duration: 150}}

    }
}
