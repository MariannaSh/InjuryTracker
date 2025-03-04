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

document.addEventListener('DOMContentLoaded', function() {
    // Добавляем обработчик событий для кнопки
    const clearDbButton = document.getElementById('clear-db-btn');
    
    if (clearDbButton) {
        clearDbButton.addEventListener('click', function() {
            if (confirm("Are you sure you want to clear the database?")) {
                fetch('/clear_db', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });
    } else {
        console.error('Button with id "clear-db-btn" not found');
    }
});

document.getElementById("clear-db-btn").addEventListener("click", function() {
    fetch('/clear_progress', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);  // Показываем сообщение об успехе или ошибке
    })
    .catch(error => {
        console.error("Error clearing database:", error);
    });
});


document.addEventListener("DOMContentLoaded", function() {
    const starCount = 30;
    const body = document.body;

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement("div");
        star.classList.add("star");
        star.style.top = Math.random() * 100 + "%";
        star.style.left = Math.random() * 100 + "%";
        body.appendChild(star);
    }
});
