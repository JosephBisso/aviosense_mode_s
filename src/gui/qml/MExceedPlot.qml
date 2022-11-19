import QtQml 2.15
import QtQuick 2.15
import QtCharts 2.15

Column {
    id: exceedRow
    property var distribution: {}
    property var smoothed: []
    property string address: ""
    property string identification: ""
    property var allCategories: [0,10,20,30,40,50,60,70,80,90,100]

    property string title
    
    property alias distChart: barChart
    property alias smoothChart: smoothedChart

    ChartView {
        id: barChart

        width: exceedRow.width 
        height: exceedRow.height / 2

        title: exceedRow.title
        animationOptions: ChartView.SeriesAnimations

        BarSeries {
            id: distributionSeries
            labelsPrecision: 1
            axisX: BarCategoryAxis {
                id: barXAxis
                categories: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
                // labelFormat:"%d %%"
            }
            axisY: ValueAxis{
                id: yAxis
                min: 0
                max: 5
                labelFormat:"%d exceeds"
            }
        }
    }

    ChartView {
        id: smoothedChart
        width: exceedRow.width 
        height: exceedRow.height / 2

        title: exceedRow.title

        LineSeries {
            id: smoothedSeries
            name: "Smooth Density course"
            color: "orange"
            width: 4
            pointsVisible: false
            axisX: ValueAxis {
                id: smoothXAxis
                min: 0
                max: 100
                tickCount: 10
                lineVisible: true
                labelFormat:"%d%% above"
            }
            axisY: ValueAxis{
                id:rightAxis
                min:0
                max:0.5
            }
        }

    }

    function update() {
        console.info("Displaying", title)
        if (distributionSeries.count > 0) {
            distributionSeries.remove(distributionSeries.at(0))
        }

        let occurrences = [] 
        for (let category of allCategories) {
            occurrences.push(distribution[category])
        }
        distributionSeries.append("Threshold Exceed Distribution", occurrences)

        let maxDensity = 0
        for (let x = 0; x < smoothed.length; x++) {
            smoothedSeries.append(x/10, smoothed[x])
            if (smoothed[x] > maxDensity) {
                maxDensity = smoothed[x] 
            }
        }        
        console.log("exceed", address, smoothed.length, occurrences.length)

        yAxis.applyNiceNumbers()

        rightAxis.max = Math.max(0.5, maxDensity + 0.1)
        rightAxis.applyNiceNumbers()
        smoothXAxis.applyNiceNumbers()


    }

    onDistributionChanged: update()
}
