function validateForm(event) {
    console.log("validateForm called"); 

    const diagnosisConfirmed = document.getElementById('diagnosis_confirmed')?.checked;
    console.log("Diagnosis confirmed:", diagnosisConfirmed); 

    const ageElement = document.getElementById('age');
    if (ageElement) {
        const age = ageElement.value;
        if (age < 5 || age > 99) {
            alert("Are you sure you need a recommendation?");
            event.preventDefault(); 
            return;
        }
    } else {
        console.error("Age element not found.");
    }

    if (!diagnosisConfirmed) {
        event.preventDefault(); 
        alert("The application is not responsible for making diagnoses and does not provide recommendations without consulting a doctor.");
    } else {
        alert("All added exercises should be performed at a comfortable pace that does not cause pain or discomfort.");
    }
}

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

document.addEventListener("DOMContentLoaded", function () {
    loadVideos();
});

function loadVideos() {
    fetch("/get_videos")
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
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
    if (!videoList) {
        console.error("Element with id 'videos_list' not found.");
        return;
    }
    
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
    const title = document.getElementById("video_title")?.value.trim();
    const link = document.getElementById("video_url")?.value.trim();
    const category = document.getElementById("video_category")?.value;

    if (!title || !link) {
        alert("Enter the title and link to the video!");
        return;
    }

    fetch("/add_video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, link, category })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
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
    const selectedCategory = document.getElementById("filter_category")?.value;

    if (!selectedCategory) {
        console.error("Filter category element not found.");
        return;
    }

    fetch("/get_videos")
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
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
    fetch(`/delete_event/${videoId}`, { method: "DELETE" })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadVideos(); 
            }
        })
        .catch(error => console.error("Delete Error:", error));
}

const modal = document.getElementById('event-modal');
const btn = document.getElementById('add-event-btn');
const closeBtn = document.getElementById('close-modal');

if (btn) {
    btn.onclick = function() {
        modal.style.display = "block";
    }
}

if (closeBtn) {
    closeBtn.onclick = function() {
        modal.style.display = "none";
    }
}

window.onclick = function(event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

document.getElementById('submit-event').addEventListener('click', function(e) {
    e.preventDefault();

    const title = document.getElementById('event-title').value.trim();
    const date = document.getElementById('event-date').value;
    const startTime = document.getElementById('event-start-time').value || "00:00";
    const endTime = document.getElementById('event-end-time').value || "00:00";
    const repeatType = document.getElementById('repeat-event').value;

    if (!title || !date) {
        alert('Title and Date are required!');
        return;
    }

    const startDateTime = `${date}T${startTime}:00`;
    const endDateTime = `${date}T${endTime}:00`;

    fetch('/add_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: title,
            start: startDateTime,
            end: endDateTime,
            repeat_type: repeatType  
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Event added successfully!');
            location.reload();
        } else {
            console.error("Error adding event:", data);
            alert('Error adding event: ' + data.message);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An error occurred while adding the event.");
    });
});

function openEventModal(el) {
    const title = el.dataset.title;
    const start = new Date(el.dataset.start);
    const end = new Date(el.dataset.end);
    const id = el.dataset.id;
    const completed = el.dataset.completed === "true";

    console.log("Event ID:", id);

    document.getElementById("view-event-status").innerText = completed ? "Completed ✅" : "Pending";
    
    const completeBtn = document.getElementById("complete-event-btn");
    completeBtn.style.display = completed ? "none" : "inline-block";

    document.getElementById("view-event-title").innerText = title;
    document.getElementById("view-event-date").innerText = start.toLocaleDateString();
    document.getElementById("view-event-time").innerText = start.toLocaleTimeString() + " - " + end.toLocaleTimeString();

    document.getElementById("view-event-title").dataset.eventId = id;

    document.getElementById("complete-event-btn").dataset.id = id;
    document.getElementById("delete-event-btn").dataset.id = id;

    document.getElementById("view-event-modal").style.display = "block";
}

document.getElementById("close-view-modal").onclick = function () {
    document.getElementById("view-event-modal").style.display = "none";
};

document.getElementById("complete-event-btn").onclick = function () {
    const id = this.dataset.id;

    fetch("/complete_user_event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event_id: id })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Marked as completed!");
            location.reload();
        }
    });
};

document.getElementById("delete-event-btn").onclick = function () {
    const id = this.dataset.id;

    if (confirm("Delete this event?")) {
        fetch(`/delete_event/${id}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("Deleted!");
                location.reload();
            }
        });
    }
};


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

window.addEventListener("DOMContentLoaded", function () {
    const progressBar = document.getElementById("progress-bar");

    if (progressBar) {
        const currentPhase = parseInt(progressBar.dataset.currentPhase);
        const totalPhases = parseInt(progressBar.dataset.totalPhases);

        if (!isNaN(currentPhase) && !isNaN(totalPhases) && totalPhases > 0) {
            const percent = (currentPhase / totalPhases) * 100;
            progressBar.style.width = percent + "%";
        }
    }
});
function submitPainProgress(event) {
    event.preventDefault(); 

    const painLevel = document.getElementById("pain_level").value;
    const eventId = document.getElementById("view-event-title").dataset.eventId;
    const exerciseCompleted = true; 

    const eventDate = document.getElementById("view-event-date").innerText;

    if (!painLevel || !eventId || !eventDate) {
        console.error("Missing pain_level, event_id or event_date");
        alert("Please provide pain level, event ID, and date.");
        return;
    }

    console.log("Pain Level:", painLevel);
    console.log("Event ID:", eventId);

    fetch("/log_event_progress", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            pain_level: painLevel,
            event_id: eventId,
            exercise_completed: exerciseCompleted,  
            event_date: eventDate 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById("view-event-modal").style.display = "none"; 
            location.reload(); 
        } else {
            console.error("Failed to log progress.");
        }
    })
    .catch(error => {
        console.error("Error: " + error.message);
    });
}

document.getElementById('log-progress-btn').addEventListener('click', function() {
    var modal = document.getElementById('pain-form-modal');
    modal.style.display = 'block';  
});

document.getElementById('close-modal').addEventListener('click', function() {
    var modal = document.getElementById('pain-form-modal');
    modal.style.display = 'none'; 
});

window.onclick = function(event) {
    var modal = document.getElementById('pain-form-modal');
    if (event.target === modal) {
        modal.style.display = 'none';  
    }
};
document.addEventListener("DOMContentLoaded", function () {
    const completeButton = document.getElementById('complete-rehab-btn');

    if (completeButton) {
        completeButton.addEventListener('click', function(event) {
            const ctx = document.getElementById("painLevelChart")?.getContext("2d");
            const painLevelChart = ctx ? Chart.getChart(ctx) : null;

            if (painLevelChart) {
                painLevelChart.data.labels = [];
                painLevelChart.data.datasets[0].data = [];
                painLevelChart.update();
            }

            fetch("/complete_rehab", {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/json"
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.success) {
                    // alert("Rehabilitation completed! Starting new injury plan.");
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Error completing rehab:', error);
            });
        });
    }
});
document.addEventListener("DOMContentLoaded", function () {
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(msg => {
        msg.style.opacity = 1;
        setTimeout(() => {
            msg.style.transition = "opacity 1s ease-out";
            msg.style.opacity = 0;
        }, 4000); // покажи 4 сек, потом исчезает
    });
});
