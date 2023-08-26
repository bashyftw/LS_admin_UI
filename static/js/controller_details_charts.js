let canvas = document.getElementById('myChart');
let ctx = canvas.getContext('2d');


let myChart = new Chart(ctx, {
    type: 'line',
    data: {
        datasets: [{
            label: 'CPU Usage',
            data: [], // replace this with your actual data for CPU usage
            borderColor: 'rgba(75, 192, 192, 1)',
            fill: false,
            yAxisID: 'y-axis-1',
        }, {
            label: 'RAM',
            data: [], // replace this with your actual data for RAM
            borderColor: 'rgba(255, 99, 132, 1)',
            fill: false,
            yAxisID: 'y-axis-1',
        }, {
            label: 'Temperature',
            data: [], // replace this with your actual data for temperature
            borderColor: 'rgba(255, 159, 64, 1)',
            fill: false,
            yAxisID: 'y-axis-2',
        }, {
            label: 'Hard Drive Free Space',
            data: [], // replace this with your actual data for hard drive free space
            borderColor: 'rgba(153, 102, 255, 1)',
            fill: false,
            yAxisID: 'y-axis-1',
        }]
    },
    options: {
        animation: {
            duration: 500, // half a second
            mode: 'dataset'
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
                    callback: function (value, index, values) {
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
                    callback: function (value, index, values) {
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
});

function updateChart(){

    // Assume new data comes in
    let newTimestamp = new Date().toISOString();
    let newCPUUsage; // replace this with your actual new CPU usage data
    let newRAM; // replace this with your actual new RAM data
    let newTemperature; // replace this with your actual new temperature data
    let newHardDriveFreeSpace; // replace this with your actual new hard drive free space data
    fetch('/get_cpu/' + controllerId)  // Replace with your actual URL
        .then(response => response.json())  // Parse the response as JSON
        .then(data => {
            console.log(data);
            newCPUUsage = data.CPU[0];
            newRAM = data.ram;
            newTemperature = data.temp;
            newHardDriveFreeSpace = data.harddrive;

            console.log(newCPUUsage, newRAM, newTemperature, newHardDriveFreeSpace)
            myChart.data.labels.push(newTimestamp);
            myChart.data.datasets[0].data.push(newCPUUsage); // CPU Usage
            myChart.data.datasets[1].data.push(newRAM); // RAM
            myChart.data.datasets[2].data.push(newTemperature); // Temperature
            myChart.data.datasets[3].data.push(newHardDriveFreeSpace); // Hard Drive Free Space

            // Remove first data point if more than 50 data points are displayed to prevent overcrowding of the chart
            // if (myChart.data.labels.length > 50) {
            //     myChart.data.labels.shift(); // remove first label
            //     myChart.data.datasets.forEach(dataset => dataset.data.shift()); // remove first data point from each dataset
            // }

            var firstTimestamp = new Date(myChart.data.labels[0]);
            var currentTimestamp = new Date(newTimestamp);
            if ((currentTimestamp - firstTimestamp) / 1000 > 120) {
                myChart.data.labels.shift(); // remove first label
                myChart.data.datasets.forEach(dataset => dataset.data.shift()); // remove first data point from each dataset
            }

            // Update chart to reflect new data
            myChart.update('none');
            // console.log(myChart.data.datasets[0].data.length);


        })  // Print the data to the console
        .catch(error => console.error('Error:', error));  // Print any errors to the console

}


setInterval(function () {
    if (controllerStatus){
       updateChart()
    }


}, 2000);
