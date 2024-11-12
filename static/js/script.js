function validateForm(event) {
    console.log("validateForm called"); // Проверка вызова функции
    const diagnosisConfirmed = document.getElementById('diagnosis_confirmed').checked;
    console.log("Diagnosis confirmed:", diagnosisConfirmed); // Проверка состояния чекбокса

    if (!diagnosisConfirmed) {
        event.preventDefault(); // Остановка отправки формы
        alert("Приложение не несет ответственности за поставление диагнозов и не выдает рекомендации без консультации врача.");
    }
}

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