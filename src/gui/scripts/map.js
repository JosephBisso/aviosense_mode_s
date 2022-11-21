WorkerScript.onMessage = function (message) {
    switch (message.type) {
        case "location":
            showLocation(message.target, message.listPoint)
            break;
        case "turbulence":
            prepareTurbulentLocation(message.target, message.listPoint)
            break;
        case "kde":
            prepareKDE(message.target, message.listPoint)
            break;
        default:
            showLocation(message.target, message.listPoint)
            break;
    }

    console.log("Method end for", message.type, ". Sync follows...")
    message.target.sync()
    console.log("Sync?", message.target, message.target.count)
    WorkerScript.sendMessage({ "toLoad": message.type })
}

function showLocation(target, listPoint) {
    console.info("Displaying line series for location")
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
            let polyLine = {
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
    for (let i = 0; i < listPoint.length; i++) {
        let address = listPoint[i].address
        let identification = listPoint[i].identification
        for (let segment of listPoint[i].segments) {
            let polyLine = {
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
    for (let i = 0; i < listPoint.length; i++) {
        let kdePoint = {
            "latitude": listPoint[i].latitude,
            "longitude": listPoint[i].longitude,
            "normedKDE": listPoint[i].normedKDE,
            "kde": listPoint[i].kde,
            "bandwidth": listPoint[i].bandwidth,
            "kdeZoneID": listPoint[i].zoneID,
            "fieldWidth": listPoint[i].fieldWidth,
            "topLeftLon": listPoint[i].topLeftLon,
            "topLeftLat": listPoint[i].topLeftLat,
            "bottomRightLon": listPoint[i].bottomRightLon,
            "bottomRightLat": listPoint[i].bottomRightLat,
            "numOfAddresses": listPoint[i].numOfAddresses
        }

        target.append(kdePoint)
    }
}
