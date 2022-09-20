import QtQml 2.15
import QtQuick 2.15
import QtCharts 2.15

ChartView {
    id: kdeExceedChart
    property var latitude: []
    property var longitude: []
    property var exceedsPerAddress: []
    property var kde: []
    animationOptions: ChartView.SeriesAnimations

    signal addressClicked(string address)
    signal addressHovered(string address, string identification, string start, string end, double r, double g, double b)
    signal resetHovered()

    LineSeries {
        id: kdeSeries
        name: "KDE"
        color: "orange"
        width: 2
        pointsVisible: false
        axisX: ValueAxis {
            id: xAxis
            min: 0; max: 100
            tickCount: 10
            lineVisible: true
            labelFormat:"%d%% above"
        }
        axisY: ValueAxis{
            id:yAxis 
            min:0
            max:1
        }
    }

    function update() {
        console.info("Displaying", title)
        let occurrences = [] 

        let maxKDE = 0
        for (let x = 0; x < kdeExceedChart.kde.length; x++) {
            kdeSeries.append(x/10, kdeExceedChart.kde[x])
            if (kdeExceedChart.kde[x] > maxKDE) {
                maxKDE = kdeExceedChart.kde[x] 
            }
        }   

        kdeExceedChart.removeAllSeries()
        for (let addressData of exceedsPerAddress) {
            let lineSeries = kdeExceedChart.createSeries(ChartView.LineSeries, `A ${addressData.address} (T ${addressData.start.toFixed(1)} - ${addressData.end.toFixed(1)})`, xAxis, yAxis)
            let r = Math.random() % 0.51, g = Math.random(), b = Math.random() 
            lineSeries.color = Qt.rgba(r, g, b, 1)
            lineSeries.width = 4
            lineSeries.style = Qt.DashLine
            lineSeries.hovered.connect(
                (point, state) => {
                    lineHovered (
                        lineSeries, state, addressData.address, addressData.identification,
                        addressData.start.toFixed(1), addressData.end.toFixed(1), r, g, b
                    )
                }
            )
            lineSeries.clicked.connect(() => {lineClicked(lineSeries, addressData.address)})

            for (let xi = 0; xi < addressData.smoothed.length; xi++) {
                lineSeries.append(xi/10, addressData.smoothed[xi])
            }
        }     

        yAxis.max = Math.max(0.5, maxKDE + 0.1)
        yAxis.applyNiceNumbers()

        xAxis.applyNiceNumbers()

    }

    function lineHovered(lineSeries, hovered, address, identification, start, end, r, g, b) {
        if(hovered) {
            lineSeries.style = Qt.DashDotDotLine
            lineSeries.width = 6
            addressHovered(address, identification, start, end, r, g, b)
        } else {
            lineSeries.width = 4
            lineSeries.style = Qt.DashLine
            resetHovered()
        }

    }

    function lineClicked(lineSeries, address) {
        let name = lineSeries.name
        console.log("Clicked kde Line for", name, " >> Address:", address)
        kdeExceedChart.addressClicked(address)
    }

    onKdeChanged: update()
}
