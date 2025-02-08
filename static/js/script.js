function validateForm(event) {
    console.log("validateForm called"); // Проверка вызова функции

    // Проверка состояния чекбокса
    const diagnosisConfirmed = document.getElementById('diagnosis_confirmed').checked;
    console.log("Diagnosis confirmed:", diagnosisConfirmed); // Проверка состояния чекбокса

    // Проверка возраста
    
    // const age = document.getElementById('age').value;
    // if (age < 1 || age > 100) {
    //     alert("Are you sure you need a recommendation?");
    //     event.preventDefault(); // Остановка отправки формы
    //     return;
    // }

    // Проверка состояния чекбокса
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


// function validateForm(event) {
//     var age = document.getElementById('age').value;
//     if (age < 1 || age > 100) {
//         alert("Please enter a valid age between 1 and 100.");
//         event.preventDefault();
//     }
// }

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth', // Вид "месяц"
        selectable: true,             // Возможность выбора даты
        editable: true,               // Возможность редактирования событий
        headerToolbar: {              // Настройка верхней панели
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: '/get_events',        // URL для загрузки событий с сервера
        dateClick: function(info) {   // Добавление события при клике на дату
            let eventName = prompt("Введите название события (например, Лекарство, Тренировка):");
            if (eventName) {
                fetch('/add_event', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: eventName,
                        date: info.dateStr
                    })
                }).then(response => response.json())
                  .then(data => {
                      if (data.success) {
                          calendar.addEvent({ title: eventName, start: info.dateStr });
                          alert('Событие добавлено!');
                      } else {
                          alert('Не удалось добавить событие.');
                      }
                  });
            }
        },
        eventClick: function(info) {  // Окно с подробностями при клике на событие
            alert('Событие: ' + info.event.title + '\nДата: ' + info.event.start.toLocaleDateString());
        }
    });
    calendar.render();
});
