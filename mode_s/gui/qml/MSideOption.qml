import QtQml
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Qt5Compat.GraphicalEffects
import QtQml.Models
import "qrc:/scripts/Constants.js" as Constants


ColumnLayout {
    id: rootSideOption
    property url img_src: "qrc:/img/database.png"
    property string title: "Title"
    property ListModel options: ListModel{}
    property int leftMarginContent: 15
    property bool folded: false
    property ListModel foldedItems
    property ListModel emptyListModel: ListModel{}
    spacing: 10

    function toogle() {
        if (rootSideOption.folded) {
             options = foldedItems
        } else {
            foldedItems = options
            options = emptyListModel
        }
        rootSideOption.folded = !rootSideOption.folded
    }

    function close() {
        if (rootSideOption.folded) {return}
        foldedItems = options
        options = emptyListModel
        rootSideOption.folded = true
    }

    Rectangle {
        id: rowClickable
        Layout.bottomMargin: 10
        height:childrenRect.height
        width: childrenRect.width + 10
        radius: 15
        color: "transparent"

        border {
            width: 2
            color: "transparent"
        }

        RowLayout {
            id: titleRow
            spacing: 50
            Image {
                id: img
                source: img_src
                sourceSize.width: 50
                sourceSize.height: 50
                Layout.alignment: Qt.AlignLeft

                ColorOverlay {
                    id: fileOverlay
                    source: img
                    anchors.fill: img
                    color: Constants.FONT_COLOR
                }
            }

            Label {
                text: title
                font: Constants.FONT_BIG
                color: Constants.FONT_COLOR
                Layout.alignment: Qt.AlignRight
                Layout.fillWidth: true
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: titleRow
            enabled: true
            hoverEnabled: true
            z: 1
    
    
            onEntered: {rowClickable.border.color = Constants.GLASSY_BACKGROUND; cursorShape = Qt.PointingHandCursor}
            onExited: {rowClickable.border.color = "transparent"; cursorShape = Qt.ArrowCursor}
            onPressed: {rowClickable.color = Constants.GLASSY_BACKGROUND}
            onReleased: {rowClickable.color = "transparent"}
            onClicked:
                (event) => {
                    rootSideOption.focus = true
                    if (event.button === Qt.LeftButton) {
                        rootSideOption.toogle()
                    }
                }
        }

    }

    Repeater {
        model: rootSideOption.options
        delegate: Rectangle {
            id: rectDelegate
            height: 75
            width: 4/5 * scrollOptions.width 
            radius: 10
            color: Constants.GLASSY_BACKGROUND
            clip: true
            Layout.leftMargin: rootSideOption.leftMarginContent

            Label{
                anchors {
                    left: rectDelegate.left
                    top: rectDelegate.top
                    margins: 5
                }
                text: option_name
                font: Constants.FONT_MEDIUM
                color: Constants.FONT_COLOR
            }

            TextEdit {
                anchors {
                    horizontalCenter: rectDelegate.horizontalCenter
                    verticalCenter: rectDelegate.verticalCenter

                    verticalCenterOffset: 10
                }
                text: option_value
                font: Constants.FONT_SMALL
                color: Constants.FONT_COLOR

            }
        }
    }
}
