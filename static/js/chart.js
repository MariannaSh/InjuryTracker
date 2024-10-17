document.addEventListener("DOMContentLoaded", function () {
    // Get the context of the canvas element
    const ctx = document.getElementById('painLevelChart').getContext('2d');
    
    // Retrieve pain levels and dates from hidden elements
    const painLevels = JSON.parse(document.getElementById('painLevels').textContent);
    const dates = JSON.parse(document.getElementById('dates').textContent);
    
    // Create the line chart
    const painLevelChart = new Chart(ctx, {
        type: 'line',  // Change to line chart
        data: {
            labels: dates,  // Dates from database
            datasets: [{
                label: 'Pain Level',
                data: painLevels,  // Pain levels from database
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: false,  // Do not fill the area under the line
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Pain Level'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
});
