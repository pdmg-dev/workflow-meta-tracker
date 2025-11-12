// app/static/scripts/presence.js
const socket = io("/presence");

socket.on("user_online", function (data) {
    const userRow = document.querySelector(
        `.user-row[data-user-id="${data.user_id}"]`,
    );
    if (userRow) {
        const statusCell = userRow.querySelector(".status-badge");
        statusCell.innerHTML = '<span class="badge bg-success">Online</span>';
    }
});

// Update status badge if a user comes offline
socket.on("user_offline", function (data) {
    const userRow = document.querySelector(
        `.user-row[data-user-id="${data.user_id}"]`,
    );
    if (userRow) {
        const statusCell = userRow.querySelector(".status-badge");
        statusCell.innerHTML =
            '<span class="badge bg-secondary">Offline</span>';
    }
});
