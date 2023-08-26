let ctx = document.getElementById('myChart').getContext('2d');


const animation = {
    x: {
        type: 'number',
        easing: 'linear',
    },
    y: {
        type: 'number',
        easing: 'linear',

    },
    mode: 'dataset'
};

const config = {
    type: 'line',
    data: {
        datasets: [{
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            radius: 0,
            label: 'CPU Usage',
            yAxisID: 'y-axis-1',
        },
            {
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                radius: 0,
                label: 'RAM',
                yAxisID: 'y-axis-1',
            },
            {
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                radius: 0,
                label: 'Temperature',
                yAxisID: 'y-axis-2',
            },
            {
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                radius: 0,
                label: 'Hard Drive Free Space',
                yAxisID: 'y-axis-2',
            }]
    },
    options: {
        animation,
        interaction: {
            intersect: false
        },
        plugins: {
            legend: false
        },
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'second'
                }
            },
            'y-axis-1': {
                type: 'linear',
                display: true,
                position: 'left',
                beginAtZero: true,
                max: 100,
                ticks: {
                    callback: function(value, index, values) {
                        return value + '%';
                    }
                },
            },
            'y-axis-2': {
                type: 'linear',
                display: true,
                position: 'right',
                beginAtZero: true,
                // You can adjust these values according to your data
                min: 0,
                max: 100,
                // As we've used the same type of scale (linear) for both y-axes, we need to scale the y-axis-2 manually
                ticks: {
                    callback: function(value, index, values) {
                        return value + '°C';
                    }
                },
                // This ensures that y-axis-2 line is on the right
                grid: {
                    drawOnChartArea: false, // only want the grid lines for one axis to show up
                },
            },
        }
    }
};

let myChart = new Chart(ctx, config);


function randomIntFromInterval(min, max) { // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min)
}

setInterval(function() {
    // Assume new data comes in

    let newTimestamp = new Date().toISOString();
    let newCPUUsage = randomIntFromInterval(10, 40); // replace this with your actual new CPU usage data
    let newRAM = randomIntFromInterval(0, 20); // replace this with your actual new RAM data
    let newTemperature = randomIntFromInterval(40, 80); // replace this with your actual new temperature data
    let newHardDriveFreeSpace = randomIntFromInterval(60, 65); // replace this with your actual new hard drive free space data

    // Add new data to chart
    myChart.data.labels.push(newTimestamp);
    myChart.data.datasets[0].data.push(newCPUUsage); // CPU Usage
    myChart.data.datasets[1].data.push(newRAM); // RAM
    myChart.data.datasets[2].data.push(newTemperature); // Temperature
    myChart.data.datasets[3].data.push(newHardDriveFreeSpace); // Hard Drive Free Space

    // Remove first data point if more than 50 data points are displayed to prevent overcrowding of the chart
    if (myChart.data.labels.length > 50) {
        myChart.data.labels.shift(); // remove first label
        myChart.data.datasets.forEach(dataset => dataset.data.shift()); // remove first data point from each dataset
    }

    // Update chart to reflect new data
    myChart.update({
        duration: 0,
        lazy: false,
        easing: 'easeOutBounce'
    });
    console.log("update")

}, 1000);
