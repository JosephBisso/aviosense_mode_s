import QtQml.Models 2.15

ListModel {
    ListElement {
        option_name: "Address"
        option_value: "All"
        option_id:"address"
        option_type:"range"
    }
    ListElement {
        option_name: "BDS"
        option_value: "All"
        option_id:"bds"
        option_type:"range"
    }
    ListElement {
        option_name: "Duration Limit"
        option_value: "All"
        option_id:"duration_limit"
        option_type:"value"
    }
    ListElement {
        option_name: "ID"
        option_value: "None"
        option_id:"id"
        option_type:"range"
    }
    ListElement {
        option_name: "Latitude"
        option_value: "None"
        option_id:"latitude"
        option_type:"range"
    }
    ListElement {
        option_name: "Limit"
        option_value: "3000000"
        option_id:"limit"
        option_type:"value"
    }
    ListElement {
        option_name: "Longitude"
        option_value: "None"
        option_id:"longitude"
        option_type:"range"
    }
    ListElement {
        option_name: "Threads"
        option_value: "None"
        option_id:"dbthreads"
        option_type:"range"
    }
}
