import QtQuick 2.15
import QtGraphicalEffects 1.15

import "qrc:/scripts/Constants.js" as Constants

MButton {
    property url img_src: "qrc:/img/play.png"
    mFont: Constants.FONT_MEDIUM
    mTextColor: "white"
    width: 50
    height: width
    radius: width/2

    Image {
        id: img
        source: img_src
        sourceSize.width: 25
        sourceSize.height: 25
        anchors.centerIn: parent

        ColorOverlay {
            id: fileOverlay
            source: img
            anchors.fill: img
            color: mTextColor
        }
    }

}
