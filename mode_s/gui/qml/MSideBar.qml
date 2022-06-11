// import QtQml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQml.Models
import "qrc:/scripts/Constants.js" as Constants

Drawer {
    id: rootSideBar
    width: {
        if (rootWindow.width > rootWindow.minimumWidth ) {return 0.95 * rootWindow.width}
        else {return 0.95 * rootWindow.minimumWidth}
    }
    height: rootWindow.height 

    property int leftMarginTitle: 50
    property int verticalMarginItems: 20

    background: Rectangle {
        anchors.fill: parent
        color: Constants.BACKGROUND_COLOR2

        border {
            width: 1
            color: "black"
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

    ScrollView {
        id: scrollOptions
        width: 1/2 * rootSideBar.width
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
                title: "Data set"
                Layout.fillWidth: true
                options: ListModel {
                    ListElement {
                        option_name: "Address"
                        option_value: "All"
                    }
                    ListElement {
                        option_name: "Latitude"
                        option_value: "All"
                    }
                    ListElement {
                        option_name: "Longitude"
                        option_value: "All"
                    }
                    ListElement {
                        option_name: "BDS"
                        option_value: "All"
                    }
                    ListElement {
                        option_name: "Limit"
                        option_value: "3000000"
                    }
                }
            }

            Rectangle {
                width: 3/4 * rootSideBar.width
                height: 3
                radius: 3
                color: Constants.FONT_COLOR
            }

            MSideOption {
                id: settings
                img_src: "qrc:/img/settings.png"
                title: "Computing"
                Layout.fillWidth: true

                options: ListModel {
                    ListElement {
                        option_name: "Number of Threads"
                        option_value: "Automatic"
                    }
                    ListElement {
                        option_name: "Median Filter"
                        option_value: "7"
                    }
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
