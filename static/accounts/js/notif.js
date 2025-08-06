const messageQueue = [];
let showing = false;

function showNotification(message, type = "error") {
  messageQueue.push({ message, type });
  if (!showing) {
    displayNextNotification();
  }
}

function displayNextNotification() {
  if (messageQueue.length === 0) return;

  showing = true;
  const { message, type } = messageQueue.shift();

  const notification = document.getElementById("notification");
  const text = document.getElementById("notification-text");
  const title = document.getElementById("notification-title");

  text.innerText = message;
  notification.className = "notification";
  notification.classList.add("notification--" + type);

  if (type === "success") {
    title.innerText = "پیام";
  } else if (type === "error") {
    title.innerText = "ارور";
  } else {
    title.innerText = "";
  }

  notification.style.display = "flex";

  setTimeout(() => {
    closeNotification();
    displayNextNotification(); // Show next
  }, 4000);
}

function closeNotification() {
  const notification = document.getElementById("notification");
  notification.style.display = "none";
  showing = false;
}
