import QtQuick 2.15
import QtQml 2.15

MouseArea {
    id: selectArea

    property var control: parent
    property Rectangle highlightItem : null

    anchors.fill: control
    cursorShape: Qt.CrossCursor
    
    onPressed: {
        if (highlightItem !== null) {
            highlightItem.destroy () 
        }
        highlightItem = highlightComponent.createObject (selectArea, {
            "x" : mouse.x, "y" : mouse.y,
            "width": 1, "heigth": 1
        });
    }
    onPositionChanged: {
        highlightItem.width = (Math.abs (mouse.x - highlightItem.x))  
        highlightItem.height = (Math.abs (mouse.y - highlightItem.y))  
    }
    onReleased: {
        let rectArea = Qt.rect(highlightItem.x, highlightItem.y, highlightItem.width, highlightItem.height)
        control.zoomIn(rectArea)
        highlightItem.destroy () 
    }

    onDoubleClicked: {
        control.zoomReset()
    }

    Component {
        id: highlightComponent

        Rectangle {
            color: "blue"
            opacity: 0.2
        }
    }
}
