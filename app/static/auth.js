async function authRequest(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    throw new Error(Array.isArray(detail) ? detail.map(item => item.msg).join(", ") : detail || "Request failed");
  }
  return data;
}

const authForm = document.querySelector("#loginForm, #registerForm");
const authMode = document.body.dataset.authMode;

if (authForm) {
  authForm.addEventListener("submit", async event => {
    event.preventDefault();
    const form = event.currentTarget;
    const values = Object.fromEntries(new FormData(form));
    const message = form.querySelector(".form-message");
    const submit = form.querySelector('button[type="submit"], button:not([type])');
    message.textContent = "";
    message.classList.remove("error");
    submit.disabled = true;
    try {
      if (authMode === "register") {
        await authRequest("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(values)
        });
        window.location.assign("/login?registered=1");
        return;
      }
      await authRequest("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values)
      });
      window.location.assign("/dashboard");
    } catch (error) {
      message.textContent = error.message;
      message.classList.add("error");
    } finally {
      submit.disabled = false;
    }
  });
}

if (authMode === "login" && new URLSearchParams(window.location.search).has("registered")) {
  const notice = document.querySelector("#authNotice");
  notice.textContent = "Your account is ready. Sign in to submit and track a job.";
}
if (authMode === "login" && new URLSearchParams(window.location.search).has("password")) {
  const notice = document.querySelector("#authNotice");
  notice.textContent = "Password updated. Sign in again with your new password.";
}
