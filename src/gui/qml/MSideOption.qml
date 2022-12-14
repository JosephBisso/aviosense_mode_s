import QtQml 2.15
import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15
import QtQml.Models 2.15
import "qrc:/scripts/constants.js" as Constants


ColumnLayout {
    id: rootSideOption
    property url img_src: "qrc:/img/database.png"
    property string title: "Title"
    property int leftMarginContent: 15
    property bool folded: false
    property string code: "code"
    property ListModel foldedItems
    property ListModel options: ListModel{}
    property ListModel emptyListModel: ListModel{}
    spacing: 10

    function toogle() {
        rootSideOption.folded = !rootSideOption.folded
    }

    function close() {
        if (rootSideOption.folded) {return}
        rootSideOption.folded = true
    }

    function getData() {
        let allData = {}

        for(let i = 0; i < allOptions.count; i++) {
            let option = allOptions.itemAt(i)
            if(option.textField.text) {
                option.value = option.textField.text
            }
            if (option.value.indexOf('-') == -1) {
                allData[option.identification] = option.value
            } else {
                let min_max = option.value.split('-')
                let min = min_max[0]
                let max = min_max[1]
                allData[option.identification + "_min"] = min
                allData[option.identification + "_max"] = max
            }
        }

        let allDataJson = JSON.stringify(allData)
        console.log("All Data", title, allDataJson)
        return allData
    }

    signal edited()

    Component.onCompleted: {rootSideOption.close()}
    Component.onDestruction: {
        console.info(`Saving Configurations for ${title}...`)
        for(let i = 0; i < allOptions.count; i++) {
            let option = allOptions.itemAt(i)
            let value = option.value
            let key = option.identification
            
            appSettings.setValue(key, value)
        }
    }

    Rectangle {
        id: rowClickable
        Layout.bottomMargin: 10
        height:childrenRect.height
        width: childrenRect.width + 10
        radius: 15
        color: "transparent"

        border {
            width: Constants.BORDER_WIDTH
            color: "transparent"
        }

        RowLayout {
            id: titleRow
            spacing: 50
            Image {
                id: img
                source: img_src
                sourceSize.width: 50
                sourceSize.height: 50
                Layout.alignment: Qt.AlignLeft

                ColorOverlay {
                    id: fileOverlay
                    source: img
                    anchors.fill: img
                    color: Constants.FONT_COLOR
                }
            }

            Label {
                text: title
                font: Constants.FONT_BIG
                color: Constants.FONT_COLOR
                Layout.alignment: Qt.AlignRight
                Layout.fillWidth: true
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: titleRow
            enabled: true
            hoverEnabled: true
            z: 1
    
    
            onEntered: {rowClickable.border.color = Constants.GLASSY_BACKGROUND; cursorShape = Qt.PointingHandCursor}
            onExited: {rowClickable.border.color = "transparent"; cursorShape = Qt.ArrowCursor}
            onPressed: {rowClickable.color = Constants.GLASSY_BACKGROUND}
            onReleased: {rowClickable.color = "transparent"}
            onClicked:
                (event) => {
                    rootSideOption.focus = true
                    if (event.button === Qt.LeftButton) {
                        rootSideOption.toogle()
                    }
                }
        }

    }

    Repeater {
        id: allOptions
        model: rootSideOption.options
        delegate: Rectangle {
            id: rectDelegate
            objectName: "option_element"
            height: 100
            width: 4/5 * scrollOptions.width 
            radius: 10
            color: Constants.GLASSY_BACKGROUND
            clip: true
            visible: !rootSideOption.folded
            property string name: option_name
            property string identification: option_id
            property string value: appSettings.value(identification, option_value)
            property alias textField: delegateTextField
            Layout.leftMargin: rootSideOption.leftMarginContent

            Label{
                anchors {
                    left: rectDelegate.left
                    top: rectDelegate.top
                    margins: 10
                }
                text: option_name
                font: Constants.FONT_MEDIUM
                color: Constants.FONT_COLOR
            }

            TextField {
                id: delegateTextField
                property string textBefore
                property RegularExpressionValidator rangeValidator: RegularExpressionValidator{regularExpression: /^[aA]((ll)|uto)$|^[Nn]one$|^\d+(-\d+)?$/}
                property RegularExpressionValidator valueValidator: RegularExpressionValidator{regularExpression: /^[aA]((ll)|uto)$|^[Nn]one$|^\d+$/}
                property RegularExpressionValidator stringValidator: RegularExpressionValidator{regularExpression: /.*/}
                anchors {
                    horizontalCenter: rectDelegate.horizontalCenter
                    verticalCenter: rectDelegate.verticalCenter

                    verticalCenterOffset: 20
                }
                placeholderText: rectDelegate.value
                font: Constants.FONT_SMALL
                color: Constants.FONT_COLOR
                readOnly: false
                echoMode: {option_id === "password"? TextInput.PasswordEchoOnEdit : TextInput.Normal}
                validator: {
                    if (option_type === "string") {return stringValidator}
                    return option_type === "range" ? rangeValidator : valueValidator 
                }
                onFocusChanged: delegateTextField.accepted()
                onAccepted: {
                    if(textBefore !== text) {
                        textBefore = text
                        rootSideOption.edited()
                    }
                }

                background: Rectangle{
                    anchors.fill: parent
                    color: "transparent"
                }
            }
        }
    }
}
