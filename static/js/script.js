function validateForm(event) {
    console.log("validateForm called"); 
    
    const diagnosisConfirmed = document.getElementById('diagnosis_confirmed').checked;
    console.log("Diagnosis confirmed:", diagnosisConfirmed); 

    const age = document.getElementById('age').value;
    if (age < 5 || age > 99) {
        alert("Are you sure you need a recommendation?");
        event.preventDefault(); 
        return;
    }

    if (!diagnosisConfirmed) {
        event.preventDefault(); 
        alert("The application is not responsible for making diagnoses and does not provide recommendations without consulting a doctor.");
    } else {
        alert("All added exercises should be performed at a comfortable pace that does not cause pain or discomfort.");
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


document.addEventListener("DOMContentLoaded", function () {
    loadVideos();
});

function loadVideos() {
    fetch("/get_videos")
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayVideos(data.videos);
            } else {
                console.error("Error loading video:", data);
            }
        })
        .catch(error => console.error("Request error:", error));
}

function displayVideos(videos) {
    const videoList = document.getElementById("videos_list");
    videoList.innerHTML = ""; 
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

function deleteVideo(videoId) {
    fetch(`/delete_video/${videoId}`, { method: "DELETE" })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadVideos(); 
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
                    console.error('Failed to load events!');
                }
            }
        ],
        headerToolbar: {            
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        dateClick: function(info) {   
            let eventName = prompt("Enter the event name (e.g., Medication, Workout):");
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
                          alert('Event added!');
                      } else {
                          alert('Failed to add event.');
                      }
                  }).catch(error => {
                      console.error('Error adding event:', error);
                  });
            }
        },
        eventClick: function(info) { 
            alert('Event: ' + info.event.title + '\nDate: ' + info.event.start.toLocaleDateString());
        }
    });

    calendar.render();
});
document.addEventListener("DOMContentLoaded", function () {
    let calendarEl = document.getElementById("calendar");

    if (!calendarEl) {
        console.error("Calendar container not found!");
        return;
    }

    fetch("/get_events")
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let calendar = new FullCalendar.Calendar(calendarEl, {
                    initialView: "dayGridMonth",
                    headerToolbar: {
                        left: "prev,next today",
                        center: "title",
                        right: "dayGridMonth,timeGridWeek,timeGridDay",
                    },
                    events: data.events,
                    editable: true,
                    dateClick: function (info) {
                        let eventName = prompt("Enter the event name:");
                        if (eventName) {
                            fetch("/add_event", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({
                                    title: eventName,
                                    start: info.dateStr
                                })
                            })
                                .then((response) => response.json())
                                .then((data) => {
                                    if (data.success) {
                                        calendar.addEvent({
                                            id: data.id,
                                            title: eventName,
                                            start: info.dateStr,
                                            backgroundColor: "#007bff", 
                                            borderColor: "#007bff"
                                        });
                                        alert("Event added!");
                                    } else {
                                        alert("Error: " + data.message);
                                    }
                                })
                                .catch(error => console.error("Event addition error: ", error));
                        }
                    },
                    eventClick: function (info) {
                        if (info.event.extendedProps.completed) {
                            if (confirm("Delete this event?")) {
                                fetch("/delete_event/" + info.event.id, { method: "DELETE" })
                                    .then((response) => response.json())
                                    .then((data) => {
                                        if (data.success) {
                                            info.event.remove();
                                            alert("Event deleted!");
                                        } else {
                                            alert("Error: " + data.message);
                                        }
                                    })
                                    .catch((error) => console.error("Deletion error:", error));
                            }
                        } else {
                            if (confirm("Mark the event as completed?")) {
                                fetch("/complete_user_event", {
                                    method: "POST",
                                    headers: { "Content-Type": "application/json" },
                                    body: JSON.stringify({ event_id: info.event.id }),
                                })
                                    .then((response) => response.json())
                                    .then((data) => {
                                        if (data.success) {
                                            info.event.setExtendedProp("completed", true);
                                            info.event.setProp("classNames", ["fc-event-completed"]);
                                            alert("Event marked as completed!");
                                        } else {
                                            alert("Error: " + data.message);
                                        }
                                    })
                                    .catch((error) => console.error("Error updating event:", error));
                            }                            
                        }
                    },

                    eventColor: "#007bff", 
                });

                calendar.render();
            }
        })
        .catch((error) => console.error("Ошибка загрузки событий:", error));
});



document.addEventListener("DOMContentLoaded", function() {
    const passwordForm = document.getElementById("change-password-form");

    if (passwordForm) {
        passwordForm.addEventListener("submit", function(event) {
            event.preventDefault(); 

            const formData = new FormData(passwordForm);
            const passwordError = document.getElementById("passwordError");

            fetch("/change_password", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showPasswordError(data.error); 
                } else {
                    alert("Password successfully changed!");
                    window.location.reload(); 
                }
            })
            .catch(error => {
                console.error("Error:", error);
                showPasswordError("An error occurred. Please try again.");
            });
        });
    }
});

function showPasswordError(message) {
    let errorContainer = document.getElementById("passwordError");
    errorContainer.innerText = message;
    errorContainer.style.display = "block";
}

document.addEventListener("DOMContentLoaded", function () {
    const flashData = document.getElementById("flash-data");
    if (!flashData) return;

    const messages = JSON.parse(flashData.getAttribute("data-messages"));

    if (messages.length > 0) {
        const usernameError = messages.find(([category, message]) => category === 'error' && message.includes('Username already exists'));
        const passwordError = messages.find(([category, message]) => category === 'error' && message.includes('Password must be at least'));

        if (usernameError) {
            document.getElementById('username-error').textContent = usernameError[1];
            document.getElementById('username-error').style.display = 'block';
        }

        if (passwordError) {
            document.getElementById('password-error').textContent = passwordError[1];
            document.getElementById('password-error').style.display = 'block';
        }
    }
});

document.addEventListener("DOMContentLoaded", function () {
    function loadRecommendations() {
        fetch("/get_recommendation_for_today")
            .then(response => response.json())
            .then(data => {
                let recommendationsContainer = document.getElementById("recommendations");
                if (!recommendationsContainer) {
                    console.error("Recommendations container not found!");
                    return;
                }

                recommendationsContainer.innerHTML = ""; 

                if (data.success) {
                    let phaseTitle = document.createElement("h3");
                    phaseTitle.innerText = "Current Phase:" ;
                    recommendationsContainer.appendChild(phaseTitle);

                    data.recommendations.forEach(rec => {
                        let recBlock = document.createElement("div");
                        recBlock.classList.add("recommendation-item");

                        let text = document.createElement("p");
                        text.innerHTML = rec.text;
                        recBlock.appendChild(text);

                        if (rec.image_url) {
                            let image = document.createElement("img");
                            image.src = rec.image_url;
                            image.alt = "Exercise Image";
                            image.style.maxWidth = "150px";
                            recBlock.appendChild(image);
                        }

                        if (rec.video_url) {
                            let video = document.createElement("video");
                            video.src = rec.video_url;
                            video.controls = true;
                            video.style.maxWidth = "200px";
                            recBlock.appendChild(video);
                        }

                        recommendationsContainer.appendChild(recBlock);
                    });
                } else {
                    recommendationsContainer.innerHTML = "<p>No recommendations available for today.</p>";
                }
            })
            .catch(error => console.error("Ошибка загрузки рекомендаций:", error));
    }

    loadRecommendations();

    setInterval(() => {
        let now = new Date();
        if (now.getHours() === 0 && now.getMinutes() === 0) {
            loadRecommendations();
        }
    }, 60000);
});

document.addEventListener("DOMContentLoaded", function () {
    let progressBar = document.getElementById("progress-bar");
    let currentPhase = parseInt(progressBar.getAttribute("data-current-phase"));
    let totalPhases = parseInt(progressBar.getAttribute("data-total-phases"));

    if (!isNaN(currentPhase) && !isNaN(totalPhases) && totalPhases > 0) {
        let progressPercentage = (currentPhase / totalPhases) * 100;
        progressBar.style.width = progressPercentage + "%";
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".progress-form");

    if (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault(); 

            const formData = new FormData(form);

            fetch("/add_progress", {
                method: "POST",
                body: formData
            })
            .then(response => response.json()) 
            .then(data => {
                if (data.success) {
                    alert("Progress successfully added!");
                    form.reset(); 
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred. Please try again.");
            });
        });
    }
});
