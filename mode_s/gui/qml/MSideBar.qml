// import QtQml 2.15
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml.Models 2.15
import "qrc:/scripts/Constants.js" as Constants

Drawer {
    id: rootSideBar

    property int leftMarginTitle: 50
    property int verticalMarginItems: 50
    property bool edited: false
    width: 0.95 * rootWindow.width
    height: rootWindow.height 


    background: Rectangle {
        anchors.fill: parent
        color: Constants.BACKGROUND_COLOR2

        border {
            width: Constants.BORDER_WIDTH
            color: "black"
        }
    }

    onClosed: rootSideBar.edited = false 

    function getDBData() {
        let databaseDataJson = JSON.stringify(database.getData())
        return databaseDataJson
    }

    function getEngineData() {
        let engineDataJson = JSON.stringify(settings.getData())
        return engineDataJson
    }

    function sendDbParams() {
        console.info("Transmitting data to database")
        let allData = rootSideBar.getDBData()
        __mode_s.updateDBFilter(allData)
    }

    function sendEngineParams() {
        console.info("Transmitting data to engine")
        let allData = rootSideBar.getEngineData()
        __mode_s.updateEngineFilter(allData)
    }

    function sendAllParams() {
        console.info("Transmitting data to engine and database")
        let dbData = rootSideBar.getDBData()
        let engineData = rootSideBar.getEngineData()
        __mode_s.updateDBFilter(dbData)
        __mode_s.updateEngineFilter(engineData)
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

    MIMGButton {
        id: dbButton
        anchors {
            right: parent.right
            verticalCenter: parent.verticalCenter

            rightMargin: 100
            verticalCenterOffset: -width
        }
        width: 75
        img_src: "qrc:/img/sync_db.png"
        mFont: Constants.FONT_SMALL
        property color leColor: Constants.ACCENT_COLOR2
        mDefaultColor: Constants.transparentBy(leColor, 0.5)
        mHoverColor: Qt.darker(mDefaultColor, 1.3)
        mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
        mTextColor: "white"
        mToolTipText: "Actualize DB"
        onClicked: {
            sendDbParams()
        }
    }
    MIMGButton {
        id: engineButton
        anchors {
            right: parent.right
            verticalCenter: parent.verticalCenter

            rightMargin: 100
            verticalCenterOffset: width
        }
        width: 75
        img_src: "qrc:/img/power_button.png"
        mFont: Constants.FONT_SMALL
        property color leColor: "green"
        mDefaultColor: Constants.transparentBy(leColor, 0.5)
        mHoverColor: Qt.darker(mDefaultColor, 1.3)
        mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
        mTextColor: "white"
        mToolTipText: "Start Engine"
        onClicked: {
            sendEngineParams()
        }
    }
    // MIMGButton {
    //     id: startButton
    //     anchors {
    //         right: parent.right
    //         verticalCenter: parent.verticalCenter

    //         rightMargin: 100
    //     }
    //     width: 75
    //     img_src: "qrc:/img/play.png"
    //     mFont: Constants.FONT_SMALL
    //     mDefaultColor: "green"
    //     mHoverColor: Qt.lighter(mDefaultColor, 1.2)
    //     mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
    //     mTextColor: "white"
    //     onClicked: {
    //         sendAllParams()
    //     }
    // }

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
                options: MSideOptionList{id: dbOptions}

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
                    id: engineOptions
                    ListElement {
                        option_name: "Bandwidth KDE"
                        option_value: "0.5"
                        option_id:"bandwidth"
                        option_type:"value"

                    }
                    ListElement {
                        option_name: "Data Points (Min)"
                        option_value: "2000"
                        option_id:"mindatapoints"
                        option_type:"value"

                    }
                    ListElement {
                        option_name: "Filter"
                        option_value: "7"
                        option_id:"median"
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
