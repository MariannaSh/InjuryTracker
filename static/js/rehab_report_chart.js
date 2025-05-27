document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById("rehabReportChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const painLevels = window.rehabPainLevels || [];
    const rawDates = window.rehabDates || [];

    const labels = rawDates.map(date => {
        const d = new Date(date);
        return d.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "short"
        });
    });

    const dataPoints = labels.map((label, i) => ({
        x: label,
        y: painLevels[i]
    }));

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels, 
            datasets: [{
                label: "Pain Level",
                data: dataPoints,
                borderColor: "#14b8a6",
                backgroundColor: "rgba(20, 184, 166, 0.2)",
                fill: true,
                tension: 0.1,
                pointRadius: 3
            }]
        },
        options: {
            scales: {
                x: {
                    type: "category",
                    ticks: { color: "#ccc" },
                    grid: { color: "#333" }
                },
                y: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        color: "#ccc",
                        stepSize: 2
                    },
                    grid: { color: "#333" }
                }
            },
            plugins: {
                legend: {
                    labels: { color: "#03dac6", font: { size: 14 } }
                },
                tooltip: {
                    backgroundColor: "#111",
                    titleColor: "#14b8a6",
                    bodyColor: "#fff"
                }
            },
            responsive: true,
            maintainAspectRatio: true
        }
    });
});
document.addEventListener("DOMContentLoaded", function () {
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
