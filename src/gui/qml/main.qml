import QtQml 2.15
import QtQuick 2.15
import Qt.labs.settings 1.0
import QtQuick.Controls 2.15
import QtQml.WorkerScript 2.15
import "qrc:/scripts/constants.js" as Constants

ApplicationWindow {
    id: rootWindow
    x: windowsSettings.value("rootX", 0)
    y: windowsSettings.value("rootY", 0)
    width: windowsSettings.value("rootWidth", 960)
    height: windowsSettings.value("rootHeight", 720)


    minimumWidth: 960
    minimumHeight: 720
    visible: true
    title: qsTr("MODE_S Analysis | v1.0.0-beta | j.bisso-bi-ela@tu-braunschweig.de")

    background: Rectangle {
        anchors.fill: parent
        color: Constants.BACKGROUND_COLOR1
    }

    Component.onCompleted: {
        __mode_s.printFullLogPath()
        __mode_s.startDatabase()
    }

    Component.onDestruction: {
        console.info("Saving Configurations for Root Window ...")
        windowsSettings.setValue("rootX", rootWindow.x)
        windowsSettings.setValue("rootY", rootWindow.y)
        windowsSettings.setValue("rootWidth", rootWindow.width)
        windowsSettings.setValue("rootHeight", rootWindow.height)
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

    Settings {
        id: windowsSettings
        category: "windows"
    }
}
