import QtQml 2.15
import QtQuick 2.15
import Qt.labs.settings 1.0
import QtQuick.Controls 2.15
import QtQml.WorkerScript 2.15
import "qrc:/scripts/constants.js" as Constants

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
        __mode_s.startDatabase()
    }

    MSideBar {
        id: sideBar
    }

    MMainView {
        id: mainView
        anchors.fill: parent
    }

    MBusyIndicator{
        id: busyIndicator
    }

    MStatusBar {
        id: backgroudTaskIndicator
        z: 1
        anchors {
            left: parent.left
            bottom: parent.bottom

            margins: 20
        }
    }



    Settings {
        id: appSettings
        category: "parameters"
    }
}
