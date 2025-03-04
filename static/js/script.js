function validateForm(event) {
    console.log("validateForm called"); 
    
    // Проверка состояния чекбокса
    const diagnosisConfirmed = document.getElementById('diagnosis_confirmed').checked;
    console.log("Diagnosis confirmed:", diagnosisConfirmed); // Проверка состояния чекбокса

    const age = document.getElementById('age').value;
    if (age < 5 || age > 99) {
        alert("Are you sure you need a recommendation?");
        event.preventDefault(); 
        return;
    }

    // Проверка состояния чекбокса
    if (!diagnosisConfirmed) {
        event.preventDefault(); 
        alert("Приложение не несет ответственности за поставление диагнозов и не выдает рекомендации без консультации врача.");
    } else {
        alert("Все добавленные упражнения следует выполнять в комфортном для вас режиме, не вызывающем боли или дискомфорта.");
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


// Загружаем список видео при загрузке страницы
document.addEventListener("DOMContentLoaded", function () {
    loadVideos();
});

// Функция для загрузки видео с сервера
function loadVideos() {
    fetch("/get_videos")
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayVideos(data.videos);
            } else {
                console.error("Ошибка загрузки видео:", data);
            }
        })
        .catch(error => console.error("Ошибка запроса:", error));
}

// Функция для вывода списка видео
function displayVideos(videos) {
    const videoList = document.getElementById("videos_list");
    videoList.innerHTML = ""; // Очищаем перед добавлением новых видео

    if (videos.length === 0) {
        videoList.innerHTML = "<p>No videos added.</p>";
        return;
    }

    videos.forEach(video => {
        const videoElement = document.createElement("div");
        videoElement.classList.add("video-item");
        videoElement.innerHTML = `
            <p><strong>${video.title}</strong> (${video.category})</p>
            <a href="${video.link}" target="_blank">${video.link}</a>
            <button onclick="deleteVideo(${video.id})">Remove</button>
        `;
        videoList.appendChild(videoElement);
    });
}

// Функция добавления видео
function addVideo() {
    const title = document.getElementById("video_title").value.trim();
    const link = document.getElementById("video_url").value.trim();
    const category = document.getElementById("video_category").value;

    if (!title || !link) {
        alert("Enter the title and link to the video!");
        return;
    }

    fetch("/add_video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, link, category })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadVideos();
                document.getElementById("video_title").value = "";
                document.getElementById("video_url").value = "";
            }
        })
        .catch(error => console.error("Add error:", error));
}

// Фильтр видео по категории
function filterVideos() {
    const selectedCategory = document.getElementById("filter_category").value;

    fetch("/get_videos")
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let filteredVideos = data.videos;
                if (selectedCategory !== "all") {
                    filteredVideos = filteredVideos.filter(video => video.category === selectedCategory);
                }
                displayVideos(filteredVideos);
            }
        })
        .catch(error => console.error("Filter Error:", error));
}

// Функция удаления видео
function deleteVideo(videoId) {
    fetch(`/delete_video/${videoId}`, { method: "DELETE" })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadVideos(); // Обновляем список после удаления
            }
        })
        .catch(error => console.error("Delete Error:", error));
}


document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    if (!calendarEl) {
        console.error("Calendar container not found!");
        return;
    }

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth', 
        selectable: true,             
        editable: true,             
        eventSources: [
            {
                url: '/get_events', 
                method: 'GET',
                failure: function() {
                    console.error('Не удалось загрузить события!');
                }
            }
        ],
        headerToolbar: {            
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        dateClick: function(info) {   
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
                  }).catch(error => {
                      console.error('Ошибка при добавлении события:', error);
                  });
            }
        },
        eventClick: function(info) { 
            alert('Событие: ' + info.event.title + '\nДата: ' + info.event.start.toLocaleDateString());
        }
    });

    calendar.render();
});