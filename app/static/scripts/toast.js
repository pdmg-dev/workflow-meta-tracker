document.addEventListener("DOMContentLoaded", () => {
    initToasts(document);
});

document.addEventListener("htmx:afterSwap", (e) => {
    initToasts(e.target);
});

function initToasts(container) {
    if (!container) return;
    const toastElements = container.querySelectorAll("#toastContainer .toast");
    toastElements.forEach((toastEl) => {
        if (toastEl.__shown) return; // prevent double showing
        toastEl.__shown = true;

        const toast = new bootstrap.Toast(toastEl);
        toast.show();

        toastEl.addEventListener("hidden.bs.toast", () => {
            toastEl.remove();
        });
    });
}

/**
 * Dynamically show a toast message
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
        <button type="button" class="btn-close btn-close-white me-2 m-auto"
                data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    `;

    container.appendChild(toastEl);
    initToasts(container);
}
