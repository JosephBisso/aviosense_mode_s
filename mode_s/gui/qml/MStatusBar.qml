import QtQml 2.15
import QtQuick 2.15
import QtQml.Models 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import "qrc:/scripts/constants.js" as Constants
import "qrc:/scripts/util.js" as Util

Column {
    id: statusBar
    width: Math.max((1/4) * parent.width, 475)
    height: implicitHeight + 5
    spacing: 2
    clip: true
    visible: !busyIndicator.visible

    move: Transition {
        NumberAnimation {properties: "x, y"; duration: 250}
    }
    add: Transition {
        NumberAnimation {properties: "x, y"; duration: 250}
    }


    ListModel {
        id: statusElements
    }

    Connections {
        id: statusConnection
        target: __mode_s
        function onProgressed(progressID, msg) {
            let deleting = msg.includes(Constants.END_PROGRESS_BAR)

            for (let i = 0; i < statusElements.count; i++) {
                if (!statusElements.get(i)) {continue}
                if (statusElements.get(i).progressID == progressID) {
                    if (msg.includes(Constants.END_PROGRESS_BAR)) {
                        statusElements.remove(i, 1)
                        continue
                    }
                    let cleanMsg = msg.replace(statusElements.get(i).progressID, "")
                    statusElements.get(i).message = cleanMsg
                    return
                }
            }
            if (deleting)  {return}

            let color = ""
            let leID = progressID
            switch(progressID) {
                case Constants.DATABASE:
                    color = Constants.ACCENT_COLOR2
                    break
                case Constants.ENGINE:
                    color = "lime"
                    break
                case Constants.MODE_S:
                    color = Constants.ACCENT_COLOR3
                    break
                case Constants.ID_LOCATION:
                    color = "dodgerBlue"
                    break
                case Constants.ID_TURBULENT:
                    color = "lightsalmon"
                    break
                case Constants.ID_KDE:
                    color = "cyan"
                    break
                case Constants.ID_KDE_EXCEED:
                case Constants.ID_PLOT:
                    color = "gold"
                    break
                default:
                    color = "dodgerBlue"
                    break
            }

            let cleanMsg = msg.replace(leID, "")
            let img = getImgFromId(progressID)

            statusElements.append({
                "progressID"    : progressID,
                "img"           : img,
                "message"       : cleanMsg,
                "progressColor" : color
            })
        }
    }

    function getImgFromId(progressID) {
        switch(progressID) {
            case Constants.ID_TURBULENT:
            case Constants.ID_KDE:
            case Constants.ID_LOCATION:
                return "world"
            case Constants.DATABASE:
                return "sync_db"
            case Constants.ENGINE:
                return "power_button"
            case Constants.MODE_S:
                return "home"
            case Constants.ID_PLOT:
                return "noise"
            case Constants.ID_KDE_EXCEED:
                return "gaussian-function"
            default:
                return "settings"
        }
    }

    Repeater {
        id: statusBarRepeater
        model: statusElements
        delegate: Rectangle {
            id: statusFrame
            height: 48
            width: Math.min(contentRow.width + 20, statusBar.width)
            color: Util.transparentBy(progressColor, 0.5)
            radius: 10
            border {
                width: Constants.BORDER_WIDTH
                color: progressColor
            }

            RowLayout {
                id: contentRow
                anchors {
                    top: parent.top
                    bottom: parent.bottom
                    left: parent.left
                    
                    margins: 10
                }
                width: implicitWidth

                MIMGButton {
                    id: statusButton
                    Layout.alignment: Qt.AlignVCenter
                    width: 32
                    img_src: `qrc:/img/${img}.png`
                    mFont: Constants.FONT_SMALL
                    mDefaultColor: Constants.GLASSY_BLACK_BACKGROUND
                    mHoverColor: Constants.FOREGROUND_COLOR
                    mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
                    mTextColor: "white"
                    opacity: 1
                    mToolTipText: "Show Log"
    
                    onClicked: {
                        busyIndicator.pieck(progressColor, message)
                    }
                }

                Label {
                    id: statusMsg
                    Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                    text: message
                    font: Constants.FONT_VERY_2_SMALL
                    color: "lightgrey"
                }
                MIMGButton {
                    id: closeButton
                    visible: progressID === Constants.ID_LOCATION
                    Layout.alignment: Qt.AlignVCenter
                    width: 22
                    img_src: `qrc:/img/close.png`
                    mFont: Constants.FONT_SMALL
                    mDefaultColor: "red"
                    mHoverColor: Qt.darker(mDefaultColor, 1.1)
                    mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
                    mTextColor: "black"
                    opacity: 1
                    mToolTipText: "Stop Background task"
    
                    onClicked: {
                        mainView.stopBackgroundLoading(progressID)
                    }
                }
            }
        }
    }
}
