import QtQuick 2.15
import QtGraphicalEffects 1.15

import "qrc:/scripts/constants.js" as Constants

MButton {
    id: rootButton
    property url img_src: "qrc:/img/play.png"
    mFont: Constants.FONT_MEDIUM
    mTextColor: "white"
    width: 50
    height: width
    radius: width/2
    mText: ""
    mToolTipText: "Play"

    Image {
        id: img
        source: img_src
        sourceSize.width: rootButton.width / 2
        sourceSize.height: rootButton.width / 2
        anchors.centerIn: parent

        ColorOverlay {
            id: fileOverlay
            source: img
            anchors.fill: img
            color: mTextColor
        }
    }

}
