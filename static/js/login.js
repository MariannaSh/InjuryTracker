// Функция для показа модального окна
function showModal(message) {
    const modal = document.getElementById('modal');
    const modalMessage = document.getElementById('modal-message');
    modalMessage.textContent = message; // Устанавливаем сообщение
    modal.style.display = 'block';
}

// Закрытие модального окна
document.getElementById('close-modal').onclick = function() {
    document.getElementById('modal').style.display = 'none';
};

document.getElementById('modal-ok').onclick = function() {
    document.getElementById('modal').style.display = 'none';
};

// Проверяем наличие сообщений об ошибке
const messages = JSON.parse('{{ get_flashed_messages(with_categories=true) | tojson | safe }}');
if (messages.length > 0) {
    const errorMessage = messages.find(([category]) => category === 'error');
    if (errorMessage) {
        showModal(errorMessage[1]); // Показываем модальное окно с текстом ошибки
    }

    // Отображаем ошибку под полем, если она касается имени пользователя или пароля
    const usernameError = messages.find(([category, message]) => category === 'error' && message.includes('User does not exist'));
    const passwordError = messages.find(([category, message]) => category === 'error' && message.includes('Invalid password'));

    if (usernameError) {
        document.getElementById('username-error').textContent = usernameError[1];
    }

    if (passwordError) {
        document.getElementById('password-error').textContent = passwordError[1];
    }
}
