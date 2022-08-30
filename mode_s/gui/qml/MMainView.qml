import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtQml 2.15
import "qrc:/scripts/Constants.js" as Constants

Frame {
    id: rootMainView
    property var identMap: null
    anchors.fill: parent
    background: Rectangle {
        color: "transparent"
        border.color: "transparent"
        radius: 10
    }

    function updateView(name) {
        switch(name) {
            case "world":
                rootSwipe.currentIndex = 0
                break;
            case "noise":
                rootSwipe.currentIndex = 1
                break;
        }
    } 

    function loadPlotsForFilteredAddress(filteredAddress) {

    }

    Connections {
        target: __mode_s

        function onIdentificationMapped()  {
            let identMapping = __mode_s.identMap
            console.log("Receive identMapping. Length:", Object.keys(identMapping).length)
            rootMainView.identMap = identMapping
        }
    }


    MSearchBar {
        id: searchBar
        property var suggestionsList: []
        z: 1
        anchors {
            top: parent.top
            right: verticalMenuBar.left

            margins: 20
        }
        width: Math.min(500, 1/6 * rootMainView.width)

        onFilter: (filterText) => {
            suggestionPopup.suggestions.clear()
            if (!filterText) {return}
            searchElement(filterText, suggestionPopup.suggestions)
            if (!suggestionPopup.opened) {suggestionPopup.open()}
        }

         MSuggestions {
            id: suggestionPopup

            onItemSelected: (address) => {
                plotView.preparePlotsForAddress(address)
                mapView.showAddress(address)
            }
        }
    }

    function searchElement(text, target) {
        if (!rootMainView.identMap) {return }
        let addresses = Object.keys(rootMainView.identMap)
        let identifications = Object.values(rootMainView.identMap)

        for (let i = 0; i < addresses.length; i++) {
            if (addresses[i].toString().match(text)) {target.append({
                    "address"       : addresses[i],
                    "identification": identMap[addresses[i]]
                })
            }
        }    

        if(addresses.length !== identifications.length) {console.warn("Search Result may not be valid")}
        for (let i = 0; i < identifications.length; i++) {
            if (identifications[i].toLowerCase().match(text.toLowerCase())) {target.append({
                    "address"       : addresses[i],
                    "identification": identifications[i]
                })
            }
        }    
    }

    MMapElementInfo {
        id: mapElementInfo
        z:1
        visible: {
            if (rootSwipe.currentIndex !== 0) {return false}
            else {return mapElementInfo.opened}
        } //Only forWord View
    }

    MVerticalMenuBar {
        id: verticalMenuBar
        z: 1
        anchors {
            top: parent.top
            right: parent.right

            margins: 20
        }

        onClicked: (element) => {rootMainView.updateView(element)}
    }


    MIMGButton {
        id: sideButton
        img_src: "qrc:/img/hamburger.png"
        z: 1
        anchors {
            top: parent.top
            left: parent.left

            margins: 20
        }
        mDefaultColor: Qt.rgba(0,0,0,0.8)
        mHoverColor: Constants.FOREGROUND_COLOR
        mClickColor:Qt.rgba(Constants.ACCENT_COLOR1.r, Constants.ACCENT_COLOR1.g, Constants.ACCENT_COLOR1.b, 0.5)
        mToolTipText: "Menu"
        onClicked: {
            if (sideBar.opened) {sideBar.close();return}
            sideBar.open()
        }
    }
    
    MIMGButton {
        id: saveButton
        img_src:"qrc:/img/download.png"
        z: 1
        mToolTipText: "Export"

        anchors {
            bottom: parent.bottom
            right: parent.right

            margins: 20
        }

    }

    SwipeView {
        id: rootSwipe
        orientation: Qt.Vertical
        anchors.fill: parent
        interactive: false

        MMap {
            id: mapView
            Connections {
                target: __mode_s

                function onPlotLocationReady() {
                    mapView.showLocation()
                }

                function onPlotTurbulentReady() {
                    mapView.prepareTurbulentLocation()
                }

                function onPlotHeatMapReady() {
                    mapView.prepareKDE()
                }
            }

            onAddressClicked: (address) => {
                plotView.preparePlotsForAddress(address)
            }
        }

        MPlots {
            id: plotView
            property bool isCurrentView: SwipeView.isCurrentItem

        }
    }
}
