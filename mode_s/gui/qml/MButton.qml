import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/scripts/Constants.js" as Constants

Rectangle {
    id: root

    property string mText: "Button"
    property string mToolTipText: "Action"
    property bool mEnabled: true
    property color mDefaultColor: Qt.darker(Constants.BACKGROUND_COLOR2, 1.5)
    property color mBorderColor: Constants.FONT_COLOR
    property color mHoverColor: Constants.BACKGROUND_COLOR2
    property color mClickColor: Constants.BACKGROUND_COLOR1
    property color mTextColor: Constants.FONT_COLOR
    property font mFont : Constants.FONT_BIG
    property bool mChecked: false
    property bool mCheckable: false
    property bool mManualUncheckable: false

    property alias area: mouseArea

    signal clicked()
    signal mouseEnter()
    signal mouseOut()

    onMCheckedChanged: {
        if (!mChecked) {
            root.color = mDefaultColor
        } else {
            root.color = Constants.ACCENT_COLOR1
        }
    }

    width: 150
    height: 45
    radius: 10
    color: {
        if (mEnabled) {
            if (mCheckable && mChecked) {
                return Constants.ACCENT_COLOR1
            }
            return mDefaultColor
        } else {
            return "darkgrey"
        }
    }
    border {
        width: Constants.BORDER_WIDTH
        color: mEnabled ? mBorderColor : Qt.lighter("darkgrey", 1.2)
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: mEnabled
        hoverEnabled: mEnabled
        cursorShape: Qt.PointingHandCursor

        onEntered: {
            if (!mCheckable || (mCheckable && !mChecked)) {
                root.color = mHoverColor
            }
            tooTip.visible = true
            root.mouseEnter()
        }
        onExited: {
            if (!mCheckable || (mCheckable && !mChecked)) {
                root.color = mDefaultColor
                root.border.color = mBorderColor
            }
            tooTip.visible = false
            root.mouseOut()
        }
        onPressed: root.border.color = Qt.lighter(mClickColor, 1.2)
        onReleased: root.border.color = mBorderColor
        onClicked:
            (event) => {
                if (event.button === Qt.LeftButton) {
                    if (mCheckable) {
                        if (mChecked){
                            if (mManualUncheckable) {mChecked = false}
                            root.color = Constants.ACCENT_COLOR1
                        } else {
                            mChecked = true
                        }
                    }
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

    ToolTip {
        id: tooTip
        delay: 750
        parent: root
        text: mToolTipText
        z:1

        contentItem: Text {
            text: tooTip.text
            font: Constants.FONT_SMALL
            color: mTextColor
        }

        background: Rectangle {
            color:  Constants.GLASSY_BLACK_BACKGROUND
            radius: 5
            border {
                width: Constants.BORDER_WIDTH
                color: mTextColor
            }
        }
    }
}
