document.addEventListener("DOMContentLoaded", function () {
    const painLevels = JSON.parse(document.getElementById("painLevels").textContent);
    const dates = JSON.parse(document.getElementById("dates").textContent);

    const ctx = document.getElementById("painLevelChart").getContext("2d");
    new Chart(ctx, {
        type: "line",
        data: {
            labels: dates,
            datasets: [{
                label: "Pain Level",
                data: painLevels,
                borderColor: "#14b8a6",
                borderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 6,
                backgroundColor: "rgba(20, 184, 166, 0.1)",
                tension: 0,
                fill: false,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: "#fff", font: { size: 14 } },
                },
                tooltip: {
                    backgroundColor: "#111",
                    titleColor: "#14b8a6",
                    bodyColor: "#fff",
                },
            },
            scales: {
                x: {
                    ticks: { color: "#ccc" },
                    grid: { color: "#333", lineWidth: 1.5, tickLength: 10 },
                },
                y: {
                    beginAtZero: true,
                    max: 10,
                    ticks: { color: "#ccc", stepSize: 2 },
                    grid: { color: "#333", lineWidth: 1.5, tickLength: 10 },
                    title: {
                        display: true,
                        text: "Pain Level",
                        color: "#ccc",
                    },
                },
            },
        },
    });

    // === Progress Summary ===
    const totalDays = 30;
    const daysCompleted = painLevels.length;
    const startPain = painLevels[0];
    const currentPain = painLevels[painLevels.length - 1];
    const avgDrop = startPain && currentPain ? (((startPain - currentPain) / startPain) * 100).toFixed(1) : "0";
    const rehabPhase = daysCompleted >= 20 ? 3 : daysCompleted >= 10 ? 2 : 1;
    const completionRate = Math.round((daysCompleted / totalDays) * 100);

    function getRecommendation(percent) {
        if (percent >= 90) return "You're 90% through! Final stretch — stay focused and strong.";
        if (percent >= 80) return "You're 80% done! Think about post-rehab habits.";
        if (percent >= 70) return "You're 70% through! Try adding some outdoor walks.";
        if (percent >= 60) return "You're 60% in! Keep the momentum going daily.";
        if (percent >= 50) return "Halfway there! Keep the rhythm and follow your plan daily.";
        if (percent >= 40) return "You're 40% through. Great effort — stay committed!";
        if (percent >= 30) return "Good start! Make sure you're not skipping your exercises.";
        if (percent >= 20) return "You're 20% in. Focus on building routine and habits.";
        if (percent >= 10) return "10% completed — make daily check-ins your goal.";
        return "Just started! Begin with light activity and stay consistent.";
    }

    // Progress Table
    document.getElementById("progress-summary").innerHTML = `
        <div style="max-width: 600px; margin: 20px auto; background: #111; padding: 20px; border-radius: 12px; box-shadow: 0 0 12px rgba(0, 255, 200, 0.1); color: #ccc;">
            <h3 style="color: #03dac6; margin-bottom: 15px;">Progress Summary</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 1px solid #444;">
                        <th style="text-align: left; padding: 8px;">Metric</th>
                        <th style="text-align: left; padding: 8px;">Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td style="padding: 8px;">Pain Level</td><td style="padding: 8px;">${currentPain}/10</td></tr>
                    
                    <tr><td style="padding: 8px;">Pain Reduction</td><td style="padding: 8px;">${avgDrop}%</td></tr>
                    <tr><td style="padding: 8px;">Rehab Phase</td><td style="padding: 8px;">${rehabPhase}</td></tr>
                    <tr><td style="padding: 8px;">Completion</td><td style="padding: 8px;">${completionRate}%</td></tr>
                </tbody>
            </table>
        </div>
    `;

    // Recommendation
    document.getElementById("recommendation-box").innerHTML = `
        <div style="max-width: 600px; margin: 30px auto; background: #1a1a1a; padding: 18px 20px; border-left: 4px solid #03dac6; border-radius: 8px; color: #ccc;">
            <strong>Recommendation:</strong> ${getRecommendation(completionRate)}
        </div>
    `;

    // Achievements
    const achievements = [];
    if (daysCompleted >= 1) achievements.push("🎉 Getting Started");
    if (daysCompleted >= 5) achievements.push("🥉 5-Day Streak");
    if (completionRate >= 50) achievements.push("🥈 Halfway There");
    if ((startPain - currentPain) / startPain >= 0.3) achievements.push("🔥 Pain Tamer");
    if (daysCompleted >= 14 && !painLevels.includes(0)) achievements.push("🏅 Consistency Master");
    if (completionRate >= 100) achievements.push("🏆 Rehab Completed");

    if (achievements.length > 0) {
    renderAchievements(achievements);
    }
});

function renderAchievements(achievements) {
    const rehabStart = document.getElementById("rehabStart")?.textContent || "default";
    const storageKey = `shownAchievements_${rehabStart}`;
    const shown = JSON.parse(localStorage.getItem(storageKey) || "[]");

    const html = `
    <div style="max-width: 600px; margin: 30px auto; background: #111; padding: 20px; border-radius: 12px; box-shadow: 0 0 12px rgba(0, 255, 200, 0.1); color: #ccc;">
        <h3 style="color: #03dac6; margin-bottom: 15px;">Achievements</h3>
        <div class="achievements-grid">
          ${achievements.map((a, i) => {
              const [icon, ...textParts] = a.split(' ');
              const text = textParts.join(' ');
              return `
                <div class="achievement-card fade-in" style="animation-delay: ${i * 0.15}s;">
                  <span class="achievement-icon">${icon}</span>
                  <span class="achievement-text">${text}</span>
                </div>`;
          }).join("")}
        </div>
    </div>`;

    document.getElementById("achievements-box").innerHTML = html;

    achievements.forEach((a, i) => {
        if (!shown.includes(a)) {
            setTimeout(() => showAchievementToast(a), i * 600);
            shown.push(a);
        }
    });
    localStorage.setItem(storageKey, JSON.stringify(shown));
}

// document.addEventListener('DOMContentLoaded', function() {
//     const clearProgressButton = document.getElementById('clear-db-btn');

//     if (clearProgressButton) {
//         clearProgressButton.addEventListener('click', function() {
//             if (confirm("Вы уверены, что хотите очистить прогресс?")) {
//                 fetch('/clear_progress', {  
//                     method: 'POST',
//                     headers: { 'Content-Type': 'application/json' }
//                 })
//                 .then(response => response.json())
//                 .then(data => {
//                     alert(data.message); 
//                     location.reload(); 
//                 })
//                 .catch(error => {
//                     console.error('Ошибка при очистке прогресса:', error);
//                 });
//             }
//         });
//     } else {
//         console.error('Кнопка с id "clear-db-btn" не найдена.');
//     }
// });

function showAchievementToast(text) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `🏆 New Achievement: <strong>${text}</strong>`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("show");
    }, 100);

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
