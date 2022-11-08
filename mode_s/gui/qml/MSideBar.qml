// import QtQml 2.15
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml.Models 2.15
import "qrc:/scripts/constants.js" as Constants
import "qrc:/scripts/util.js" as Util

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

    function lockButtons() {
        dbButton.mEnabled = false
        engineButton.mEnabled = false
    }

    function unlockButtons() {
        dbButton.mEnabled = true
        engineButton.mEnabled = true
    }

    function getDBData() {
        let databaseDataJson = JSON.stringify(database.getData())
        return databaseDataJson
    }

    function getEngineData() {
        let engineDataJson = JSON.stringify(settings.getData())
        return engineDataJson
    }

    function getLoginData() {
        let loginDataJson = JSON.stringify(logins.getData())
        return loginDataJson
    }

    function getDBColumnsName() {
        let dbColumnName = JSON.stringify(db_columns.getData())
        return dbColumnName
    }

    function sendDbParams() {
        sendLoginParams()
        sendDBColumnsName()
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

    function sendLoginParams() {
        console.info("Transmitting login data")
        let loginData = rootSideBar.getLoginData()
        __mode_s.updateLoginData(loginData)
    }
    function sendDBColumnsName() {
        console.info("Transmitting DB Columns Name")
        let dbColumnName = rootSideBar.getDBColumnsName()
        __mode_s.updateDBColumnsName(dbColumnName)
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
            horizontalCenter: subheader.horizontalCenter
            topMargin: 20
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
            horizontalCenter: parent.horizontalCenter
            horizontalCenterOffset: 100
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
        mDefaultColor: Util.transparentBy(leColor, 0.5)
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
        mDefaultColor: Util.transparentBy(leColor, 0.5)
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

    MIMGButton {
        id: logButton
        img_src:"qrc:/img/log.png"
        width: 75
        mToolTipText: "Open Log"
        mDefaultColor: "grey"
        mHoverColor: Constants.FOREGROUND_COLOR
        mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)

        anchors {
            top: parent.top
            right: parent.right

            rightMargin: 100
            topMargin: 50
        }

        onClicked: {
            busyIndicator.pieck("grey", "Logs")
        }
    }

    ScrollView {
        id: scrollOptions
        width: 3/8 * rootSideBar.width
        clip: true

        anchors {
            top: parent.top
            bottom: parent.bottom
            left:parent.left
            topMargin: rootSideBar.verticalMarginItems
            bottomMargin: rootSideBar.verticalMarginItems
            leftMargin: rootSideBar.leftMarginTitle
        }

        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical.stepSize: 1
        onContentHeightChanged: scrollOptions.ScrollBar.vertical.increase()

        ColumnLayout {
            id: optionColumn
            spacing: rootSideBar.verticalMarginItems
            anchors.centerIn: parent
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

            Rectangle {
                width: scrollOptions.width
                height: 3
                radius: 3
                color: Constants.FONT_COLOR
            }

            MSideOption {
                id: logins
                img_src: "qrc:/img/params.png"
                title: "Logins"
                Layout.fillWidth: true

                options: ListModel {
                    id: loginsOptions
                    ListElement {
                        option_name: "Host"
                        option_value: "tubs.skysquitter.com"
                        option_id:"host_name"
                        option_type:"string"

                    }
                    ListElement {
                        option_name: "Port"
                        option_value: "Auto"
                        option_id:"db_port"
                        option_type:"value"

                    }
                    ListElement {
                        option_name: "Database"
                        option_value: "db_airdata"
                        option_id:"db_name"
                        option_type:"string"

                    }
                    ListElement {
                        option_name: "User"
                        option_value: "tubs"
                        option_id:"user_name"
                        option_type:"string"

                    }
                    ListElement {
                        option_name: "Table"
                        option_value: "tbl_tubs"
                        option_id:"table_name"
                        option_type:"string"

                    }
                    ListElement {
                        option_name: "Password"
                        option_value: "DILAB-2022"
                        option_id: "password"
                        option_type:"string"
                    }
                }

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
                id: db_columns
                img_src: "qrc:/img/vertical.png"
                title: "DB Column Names"
                Layout.fillWidth: true

                options: ListModel {
                    id: columnsOptions
                    ListElement {
                        option_name: "Bar"
                        option_value: "bds60_barometric_altitude_rate"
                        option_id:"column_bar"
                        option_type:"string"

                    }
                    ListElement {
                        option_name: "Ivv"
                        option_value: "bds60_inertial_vertical_velocity"
                        option_id:"column_ivv"
                        option_type:"string"

                    }
                }

                onEdited: {
                    if (rootSideBar.edited){return}
                    rootSideBar.edited = true
                }
            }
        }
    }

}
