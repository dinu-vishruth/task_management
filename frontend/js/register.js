document.getElementById("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("msg");
  clearMessage(msg);

  const username = document.getElementById("username").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    const res = await fetch(API_BASE + "/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      showMessage(msg, data.message || data.error || "Registration failed.", "error");
      return;
    }
    setToken(data.access_token);
    showMessage(msg, "Account created. Redirecting…", "success");
    setTimeout(() => {
      window.location.href = "dashboard.html";
    }, 600);
  } catch (err) {
    showMessage(
      msg,
      "Network error — is the API running on " + API_BASE + "?",
      "error"
    );
  }
});
