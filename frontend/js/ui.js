/** Shared message helpers */
function showMessage(el, text, type) {
  if (!el) return;
  el.textContent = text || "";
  el.className = "message " + (type || "info");
  el.hidden = !text;
}

function clearMessage(el) {
  showMessage(el, "", "");
}
