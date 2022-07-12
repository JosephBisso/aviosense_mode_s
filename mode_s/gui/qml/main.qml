import QtQml
import QtQuick
import QtQuick.Controls
import "qrc:/scripts/Constants.js" as Constants

ApplicationWindow {
    id: rootWindow
    width: 960
    height: 720
    minimumWidth: 960
    minimumHeight: 720
    visible: true
    title: qsTr("MODE_S Analyis")

    background: Rectangle {
        anchors.fill: parent
        color: Constants.BACKGROUND_COLOR1
    }

    Component.onCompleted: {
        sideBar.open()
        __mode_s.startDatabase()
    }

    MSideBar {
        id: sideBar
        onClosed: {
            sideButton.canOpen = true
            z = -1
            sideButton.z = 1
        }
    }

    MMainView {
        id: mainView
        anchors.fill: parent
    }

    MButton {
        id: sideButton

        x: sideBar.x + sideBar.width > 0 ? sideBar.x + sideBar.width - 1/2 * width : - width / 2 
        y: rootWindow.height / 2 - height / 2
        z: -1
        width: 50
        height: width
        radius: width / 2
        mText: sideBar.x + sideBar.width > 0 ? "-<" : "->"
        mTextColor: "white"
        property bool canOpen: true

        onClicked: {
            if (sideBar.opened) {sideBar.close();return}
            if (sideButton.canOpen){
                sideButton.canOpen = false
                z = -1
                sideBar.z = 0
                sideBar.open()
            }
        }
    }

    MMenuBar {
        id: menubar
        anchors{
            top: parent.top
            horizontalCenter: parent.horizontalCenter

            topMargin: 10
        }
    }

    MIMGButton {
        id: saveButton
        img_src:"qrc:/img/download.png"
        mText: ""
        z: 1

        anchors {
            right: parent.right
            bottom: parent.bottom

            margins: 20
        }

    }
    
    MBusyIndicator{
        id: busyIndicator
    }
}
