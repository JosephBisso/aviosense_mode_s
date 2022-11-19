WorkerScript.onMessage = function (msg) {
    console.info("Starting Gui Worker. Action:", msg.action);
    var answer;
    switch (msg.action) {
        case "plot_location":
            answer = generatePolyLines(msg.argument);
            break;
    
        default:
            break;
    }

    WorkerScript.sendMessage({"action": msg.action,"answer": answer});
}

function generatePolyLines(pointList, target) {
    let allAddresses = []
    let usedColors = []
    let centerMap = QtPositioning.coordinate(0, 0)
    let radius = 5000

    for (let i = 0; i < pointList.length; i++) {
        var r, b, g, colorStr
        let addressData = {
            "address": pointList[i].address,
            "points": [],
            "color": "blue"
        }

        do {
            r = Math.floor(Math.random() * 256)
            g = Math.floor(Math.random() * 256)
            b = Math.floor(Math.random() * 256)
            colorStr = `r${r}g${g}b${b}`

        } while (usedColors.includes(colorStr))

        addressData.color = Qt.rgba(r, b, g, 1)
        usedColors.push(colorStr)

        for (let j = 0; j < pointList[i].points.length; j++) {
            let latitude = pointList[i].points[j].latitude
            let longitude = pointList[i].points[j].longitude

            let point = QtPositioning.coordinate(latitude, longitude)
            addressData.points.push(point)
        }

        addressData.points.sort((p1, p2) => { return p1.distanceTo(centerMap) - p2.distanceTo(centerMap) })
        if (addressData.length > 0) { allAddresses.push(addressData) }
    }

    for (let i = 0; i < allAddresses.length - 1; i++) {
        let segment = []
        let addressColor = allAddresses[i].color
        segment.push(allAddresses[i].points)
        let j = 0
        while (allAddresses[i].points[j].distanceTo(allAddresses[i].points[j + 1]) <= radius) {
            segment.push(allAddresses[i].points[j + 1])
            j++
        }
        target.append({
            "addressColor": addressColor,
            "segment": segment
        })
    }

    target.sync()
}
