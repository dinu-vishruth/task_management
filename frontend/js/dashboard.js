const msg = document.getElementById("msg");
const tasksEl = document.getElementById("tasks");
const whoami = document.getElementById("whoami");
const roleHint = document.getElementById("role-hint");

if (!getToken()) {
  window.location.href = "login.html";
}

document.getElementById("logout").addEventListener("click", () => {
  setToken(null);
  window.location.href = "login.html";
});

async function loadProfile() {
  const res = await fetch(API_BASE + "/auth/me", { headers: authHeaders() });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    setToken(null);
    window.location.href = "login.html";
    return null;
  }
  const u = data.user;
  whoami.textContent = u.username + " (" + u.role + ")";
  roleHint.textContent =
    u.role === "admin"
      ? "As admin, you see every user’s tasks."
      : "You only see tasks you created.";
  return u;
}

function renderTasks(tasks, containerId = "tasks") {
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  if (!tasks.length) {
    container.innerHTML = '<p class="empty">No tasks yet.</p>';
    return;
  }
  tasks.forEach((t) => {
    const div = document.createElement("div");
    div.className = "task-item";
    div.dataset.id = String(t.id);

    const meta = document.createElement("div");
    meta.className = "task-meta";
    let metaText = "Created " + (t.created_at || "?");
    if (t.author_username) metaText += " · @" + t.author_username;
    meta.textContent = metaText;

    const h = document.createElement("h3");
    h.textContent = t.title;

    const p = document.createElement("p");
    p.className = "task-desc";
    p.textContent = t.description || "(no description)";

    const actions = document.createElement("div");
    actions.className = "row-actions";
    actions.style.marginTop = "0.75rem";

    const editBtn = document.createElement("button");
    editBtn.type = "button";
    editBtn.className = "btn btn-ghost";
    editBtn.textContent = "Edit";
    editBtn.addEventListener("click", () => enterEdit(div, t));

    const delBtn = document.createElement("button");
    delBtn.type = "button";
    delBtn.className = "btn btn-danger";
    delBtn.textContent = "Delete";
    delBtn.addEventListener("click", () => removeTask(t.id));

    actions.appendChild(editBtn);
    actions.appendChild(delBtn);

    div.appendChild(meta);
    div.appendChild(h);
    div.appendChild(p);
    div.appendChild(actions);
    container.appendChild(div);
  });
}

function enterEdit(container, t) {
  container.innerHTML = "";
  const titleIn = document.createElement("input");
  titleIn.value = t.title;
  const descIn = document.createElement("textarea");
  descIn.value = t.description || "";

  const row = document.createElement("div");
  row.className = "row-actions";
  row.style.marginTop = "0.5rem";

  const save = document.createElement("button");
  save.type = "button";
  save.className = "btn btn-primary";
  save.textContent = "Save";
  save.addEventListener("click", async () => {
    await updateTask(t.id, titleIn.value, descIn.value);
  });

  const cancel = document.createElement("button");
  cancel.type = "button";
  cancel.className = "btn btn-ghost";
  cancel.textContent = "Cancel";
  cancel.addEventListener("click", () => loadTasks());

  row.appendChild(save);
  row.appendChild(cancel);

  container.appendChild(titleIn);
  container.appendChild(descIn);
  container.appendChild(row);
}

async function loadTasks() {
  clearMessage(msg);
  try {
    const res = await fetch(API_BASE + "/tasks", { headers: authHeaders() });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      showMessage(msg, data.message || "Could not load tasks.", "error");
      return;
    }

    if (data.is_admin) {
      document.getElementById("standard-tasks-card").hidden = true;
      document.getElementById("admin-tasks-card").hidden = false;
      document.getElementById("user-tasks-card").hidden = false;
      renderTasks(data.admin_tasks || [], "admin-tasks");
      renderTasks(data.user_tasks || [], "user-tasks");
    } else {
      document.getElementById("standard-tasks-card").hidden = false;
      document.getElementById("admin-tasks-card").hidden = true;
      document.getElementById("user-tasks-card").hidden = true;
      renderTasks(data.tasks || [], "tasks");
    }
  } catch (e) {
    showMessage(msg, "Network error loading tasks.", "error");
  }
}

async function updateTask(id, title, description) {
  clearMessage(msg);
  try {
    const res = await fetch(API_BASE + "/tasks/" + id, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({ title: title.trim(), description: description || "" }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      showMessage(msg, data.message || "Update failed.", "error");
      return;
    }
    showMessage(msg, "Task updated.", "success");
    await loadTasks();
  } catch (e) {
    showMessage(msg, "Network error.", "error");
  }
}

async function removeTask(id) {
  if (!confirm("Delete this task?")) return;
  clearMessage(msg);
  try {
    const res = await fetch(API_BASE + "/tasks/" + id, {
      method: "DELETE",
      headers: authHeaders(),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      showMessage(msg, data.message || "Delete failed.", "error");
      return;
    }
    showMessage(msg, "Task deleted.", "success");
    await loadTasks();
  } catch (e) {
    showMessage(msg, "Network error.", "error");
  }
}

document.getElementById("create-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearMessage(msg);
  const title = document.getElementById("new-title").value;
  const description = document.getElementById("new-desc").value;
  try {
    const res = await fetch(API_BASE + "/tasks", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ title, description }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      showMessage(msg, data.message || "Could not create task.", "error");
      return;
    }
    document.getElementById("new-title").value = "";
    document.getElementById("new-desc").value = "";
    showMessage(msg, "Task created.", "success");
    await loadTasks();
  } catch (e) {
    showMessage(msg, "Network error.", "error");
  }
});

(async function init() {
  await loadProfile();
  await loadTasks();
})();
