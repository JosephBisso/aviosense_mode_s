import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/scripts/Constants.js" as Constants

Rectangle {
    id: root

    property string mText: "Button"
    property bool mEnabled: true
    property color mDefaultColor: Qt.darker(Constants.BACKGROUND_COLOR2, 1.5)
    property color mBorderColor: Constants.FONT_COLOR
    property color mHoverColor: Constants.BACKGROUND_COLOR2
    property color mClickColor: Constants.BACKGROUND_COLOR1
    property color mTextColor: Constants.FONT_COLOR
    property font mFont : Constants.FONT_BIG

    property alias area: mouseArea

    signal clicked()
    signal mouseEnter()
    signal mouseOut()

    width: 150
    height: 45
    radius: 10
    color: mEnabled ? mDefaultColor : "darkgrey"

    border {
        width: 1
        color: mEnabled ? mBorderColor : Qt.lighter("darkgrey", 1.2)
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: mEnabled
        hoverEnabled: mEnabled


        onEntered: {root.color = mHoverColor; cursorShape = Qt.PointingHandCursor; root.mouseEnter()}
        onExited: {root.color = mDefaultColor;root.border.color = mBorderColor; cursorShape = Qt.ArrowCursor; root.mouseOut()}
        onPressed: root.border.color = Qt.lighter(mClickColor, 1.2)
        onReleased: root.border.color = mBorderColor
        onClicked:
            (event) => {
                if (event.button === Qt.LeftButton) {
                    mouseArea.focus = true
                    root.clicked()
                }
            }
    }

    Label {
        id: label
        anchors.centerIn: parent
        text: mText
        font: mFont
        color: mTextColor

    }

    Behavior on color {ColorAnimation {duration: 150}}
    Behavior on scale {NumberAnimation{duration: 150}}

}
