// Project MFA - OTP page countdown timer
// Purely visual: the real expiry check happens server-side in app.py.
// EXPIRY_SECONDS is injected by otp.html before this script loads.

(function () {
  const timerEl = document.getElementById("timer");
  if (!timerEl || typeof EXPIRY_SECONDS === "undefined") return;

  let remaining = EXPIRY_SECONDS;

  function format(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  }

  const interval = setInterval(() => {
    remaining -= 1;
    if (remaining <= 0) {
      clearInterval(interval);
      timerEl.textContent = "0:00";
      timerEl.style.color = "#B42318";
      return;
    }
    timerEl.textContent = format(remaining);
  }, 1000);

  // Auto-focus and only allow digits in the OTP field
  const otpInput = document.getElementById("otp");
  if (otpInput) {
    otpInput.addEventListener("input", () => {
      otpInput.value = otpInput.value.replace(/[^0-9]/g, "");
    });
  }
})();
