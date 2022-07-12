// import QtQml 2.15
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml.Models 2.15
import "qrc:/scripts/Constants.js" as Constants
import "qrc:/scripts/main.js" as JS

Drawer {
    id: rootSideBar

    property int leftMarginTitle: 50
    property int verticalMarginItems: 50
    property bool edited: false
    width: {
        if (rootWindow.width > rootWindow.minimumWidth ) {return 0.95 * rootWindow.width}
        else {return 0.95 * rootWindow.minimumWidth}
    }
    height: rootWindow.height 


    background: Rectangle {
        anchors.fill: parent
        color: Constants.BACKGROUND_COLOR2

        border {
            width: 1
            color: "black"
        }
    }

    function getData() {
        let allData = {}

        for (let sideOption of [database, settings]) {
            Object.assign(allData, sideOption.getData())
        }

        let allDataJson = JSON.stringify(allData)
        console.log("All Params", allDataJson)
        return allDataJson
    }

    onClosed: {
        if (rootSideBar.edited) {
            console.info("Transmitting data to database und engine")
            __mode_s.updateFilter(rootSideBar.getData())
            rootSideBar.edited = false
        }
    }

    Image {
        id: img
        anchors.fill: parent
        source: "qrc:img/background.jpg"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }

    Label {
        id: header
        height: 60
        anchors {
            top: parent.top
            right: parent.right
            topMargin: 20
            rightMargin: 40
        }
        text: "MODE_S"
        font: Constants.FONT_VERY_BIG
        color: Constants.ACCENT_COLOR1
    }
    Label {
        id: subheader
        height: 20
        anchors {
            top: header.bottom
            right: parent.right
            rightMargin: 40
        }
        text: "Data Transfer & Turbulence Prediction"
        font: Constants.FONT_SMALL
        color: "white"
    }

    ScrollView {
        id: scrollOptions
        width: 3/8 * rootSideBar.width
        clip: true

        anchors {
            top: parent.top
            bottom: params.top
            left:parent.left
            topMargin: rootSideBar.verticalMarginItems
            bottomMargin: rootSideBar.verticalMarginItems
            leftMargin: rootSideBar.leftMarginTitle
        }

        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        ColumnLayout {
            spacing: rootSideBar.verticalMarginItems
            MSideOption {
                id: database
                img_src: "qrc:/img/database.png"
                title: "Database"
                Layout.fillWidth: true
                options: MSideOptionList{}

                onEdited: {
                    if (rootSideBar.edited){return}
                    rootSideBar.edited = true
                }
            }

            Rectangle {
                width: scrollOptions.width
                height: 3
                radius: 3
                color: Constants.FONT_COLOR
            }

            MSideOption {
                id: settings
                img_src: "qrc:/img/settings.png"
                title: "Engine"
                Layout.fillWidth: true

                options: ListModel {
                    ListElement {
                        option_name: "Filter"
                        option_value: "7"
                        option_id:"median_n"
                        option_type:"value"

                    }
                    ListElement {
                        option_name: "Threads"
                        option_value: "Auto"
                        option_id: "enginethreads"
                        option_type:"value"
                    }
                }

                onEdited: {
                    if (rootSideBar.edited){return}
                    rootSideBar.edited = true
                }
            }
        }
    }

    MSideOption {
        id: params
        img_src: "qrc:/img/params.png"
        title: "Preferences"

        anchors {
            bottom: parent.bottom
            left:parent.left
            leftMargin: rootSideBar.leftMarginTitle
            bottomMargin: rootSideBar.verticalMarginItems
        }
    }

}
