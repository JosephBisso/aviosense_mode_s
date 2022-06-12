import QtQml.Models

ListModel {
    ListElement {
        option_name: "Address"
        option_value: "All"
        option_id:"address"
    }
    ListElement {
        option_name: "BDS"
        option_value: "All"
        option_id:"bds"
    }
    ListElement {
        option_name: "Interval"
        option_value: "All"
        option_id:"duration_limit"
    }
    ListElement {
        option_name: "Limit"
        option_value: "3000000"
        option_id:"limit"
    }
    ListElement {
        option_name: "Latitude MIN"
        option_value: "None"
        option_id:"latitude_minimal"
    }
    ListElement {
        option_name: "Latitude MAX"
        option_value: "None"
        option_id:"latitude_maximal"
    }
    ListElement {
        option_name: "Longitude MIN"
        option_value: "None"
        option_id:"longitude_minimal"
    }
    ListElement {
        option_name: "Longitude MAX"
        option_value: "None"
        option_id:"longitude_maximal"
    }
}
