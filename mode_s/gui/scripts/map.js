WorkerScript.onMessage = function (message) {
    switch (message.type) {
        case "location":
            showLocation(message.target, message.listPoint)
            break;
        case "turbulent":
            prepareTurbulentLocation(message.target, message.listPoint)
            break;
        case "kde":
            prepareKDE(message.target, message.listPoint)
            break;
        default:
            showLocation(message.target, message.listPoint)
            break;
    }

    message.target.sync()
    console.log("Sync?", message.target, message.target.count)
    WorkerScript.sendMessage({ "toLoad": message.type })
}

function showLocation(target, listPoint) {
    console.info("Displaying line series for location")
    target.clear()
    let usedColors = []

    for (let i = 0; i < listPoint.length; i++) {
        let r, b, g, colorStr
        do {
            r = Math.random()
            g = Math.random()
            b = Math.random()
            colorStr = `r${r}g${g}b${b}`
        } while (usedColors.includes(colorStr))

        usedColors.push(colorStr)

        let address = listPoint[i].address
        let identification = listPoint[i].identification
        for (let segment of listPoint[i].segments) {
            var polyLine = {
                "location_address": address,
                "location_identification": identification,
                "r": r,
                "g": g,
                "b": b,
                "turbulent": false,
                "segment": segment
            }

            target.append(polyLine)
        }
    }

}

function prepareTurbulentLocation(target, listPoint) {
    console.info("Displaying line series for turbulent location")
    target.clear()
    for (let i = 0; i < listPoint.length; i++) {
        let address = listPoint[i].address
        let identification = listPoint[i].identification
        for (let segment of listPoint[i].segments) {
            var polyLine = {
                "location_address": address,
                "location_identification": identification,
                "turbulent":true,
                "segment": segment
            }

            target.append(polyLine)
        }
    }
}

function prepareKDE(target, listPoint) {
    console.info("Displaying line series for KDE")
    // map.clearMapItems()
    // group.children = []
    // turbulentGroup = []
    // let usedColors = []

    // for (let i = 0; i < listPoint.length; i++) {

    //     var segment = []

    //     let address = listPoint[i].address
    //     let identification = listPoint[i].identification
    //     let lat0 = listPoint[i].points[0].latitude
    //     let long0 = listPoint[i].points[0].longitude
    //     segment.push({ "longitude": long0, "latitude": lat0, "address": address, "identification": identification })

    //     for (let j = 1; j < listPoint[i].points.length; j++) {
    //         let latitude = listPoint[i].points[j].latitude
    //         let longitude = listPoint[i].points[j].longitude

    //         var point = QtPositioning.coordinate(latitude, longitude)
    //         let lastSegmentIndex = segment.length - 1
    //         let lastSegmetPoint = QtPositioning.coordinate(segment[lastSegmentIndex].latitude, segment[lastSegmentIndex].longitude)
    //         if (lastSegmetPoint.distanceTo(point) < rootFrame.radius) {
    //             segment.push({ "longitude": point.longitude, "latitude": point.latitude, "address": address, "identification": identification })
    //             if (j == listPoint[i].points.length - 1) {
    //                 addPolyline(segment, r, g, b, "location")
    //             }
    //         } else {
    //             addPolyline(segment, r, g, b, "location")
    //             segment = []
    //             segment.push({ "longitude": point.longitude, "latitude": point.latitude, "address": address, "identification": identification })
    //         }
    //     }
    // }

    // map.addMapItemGroup(group)
}
