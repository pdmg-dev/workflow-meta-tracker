// app/static/js/toast.js
document.addEventListener("DOMContentLoaded", () => {
    // Auto-show any server-rendered toasts
    const toastElements = document.querySelectorAll("#toastContainer .toast");
    toastElements.forEach((toastEl) => {
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    });
});

/**
 * Dynamically show a toast message
 * @param {string} message - The message to display
 * @param {string} type - Bootstrap contextual class (success, danger, info, warning)
 * @param {number} delay - Optional delay in ms (default: 3000)
 */
function showToast(message, type = "info", delay = 3000) {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toastEl = document.createElement("div");
    toastEl.className = `toast align-items-center text-bg-${type} border-0`;
    toastEl.role = "alert";
    toastEl.setAttribute("aria-live", "assertive");
    toastEl.setAttribute("aria-atomic", "true");
    toastEl.setAttribute("data-bs-autohide", "true");
    toastEl.setAttribute("data-bs-delay", delay);

    toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;

    container.appendChild(toastEl);

    const toast = new bootstrap.Toast(toastEl);
    toast.show();

    toastEl.addEventListener("hidden.bs.toast", () => {
        toastEl.remove();
    });
}
