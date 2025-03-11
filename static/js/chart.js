document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById('painLevelChart').getContext('2d');
    
    const painLevels = JSON.parse(document.getElementById('painLevels').textContent);
    const dates = JSON.parse(document.getElementById('dates').textContent);

    const painLevelChart = new Chart(ctx, {
        type: 'line', 
        data: {
            labels: dates,  
            datasets: [{
                label: 'Pain Level',
                data: painLevels, 
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: false,  
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
    const clearProgressButton = document.getElementById('clear-db-btn');

    if (clearProgressButton) {
        clearProgressButton.addEventListener('click', function() {
            if (confirm("Вы уверены, что хотите очистить прогресс?")) {
                fetch('/clear_progress', {  
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message); 
                    location.reload(); 
                })
                .catch(error => {
                    console.error('Ошибка при очистке прогресса:', error);
                });
            }
        });
    } else {
        console.error('Кнопка с id "clear-db-btn" не найдена.');
    }
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
