// app/static/scripts/form-utils.js

/* Clear all field in a form */
export function clearForm(selector) {
    const form = document.querySelector(selector);
    if (!form) return;
    form.reset();
    form.querySelectorAll("input, textarea, select").forEach((element) => {
        if (element.type !== "hidden") element.value = "";
    });
}
window.clearForm = clearForm;
