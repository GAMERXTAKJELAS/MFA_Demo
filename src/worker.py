"""
Project MFA - Cloudflare Workers edition
Diploma in Computer Technology (Big Data) - TVET MARA Lumut

Same 2FA lifecycle as the local Flask version, adapted to run on
Cloudflare's Python Workers (WSGI support), so the app is reachable at a
real public URL instead of only on localhost.

What changed vs. the local version:
- Config (BOT_TOKEN, CHAT_ID, SECRET_KEY) now comes from Cloudflare
  Worker secrets/vars via `from workers import env`, instead of being
  hardcoded in the file.
- `requests` is used exactly the same way as before - Cloudflare's
  Python Workers runtime supports synchronous `requests` calls directly.
- The app is wrapped with `wsgi.entrypoint()` at the bottom so Cloudflare
  can run it.

What's unchanged and worth knowing:
- OTP storage still uses a plain in-memory dict (`active_otps`), same as
  the local version. On Workers this is not guaranteed to persist between
  every single request the way a normal always-on server would, since
  Cloudflare can spin up fresh isolates. For a solo classroom demo this
  works fine in practice (one browser tab, one logical session), but the
  "textbook correct" production fix would be Cloudflare KV (a key-value
  store with built-in per-key expiry, perfect for OTPs) - worth exploring
  as a stretch goal, see README_CLOUDFLARE.md.
"""

import time
import secrets
import requests
from flask import Flask, render_template, request, session, redirect, url_for
from workers import env, wsgi

app = Flask(__name__)

# ------------------------------------------------------------------
# 1. CONFIGURATION - pulled from Cloudflare Worker secrets / vars
#    (set these with `pywrangler secret put ...` - see README_CLOUDFLARE.md)
# ------------------------------------------------------------------

app.secret_key = env.SECRET_KEY
BOT_TOKEN = env.BOT_TOKEN
CHAT_ID = env.CHAT_ID

# Demo user accounts for this lab (username -> password).
# NOTE: In a real system you would NEVER store plaintext passwords -
# they'd be hashed and stored in a database. Simplified for lab purposes.
USERS = {
    "admin": "password123",
}

OTP_EXPIRY_SECONDS = 180

# In-memory OTP store (see module docstring above for the Workers caveat)
active_otps = {}


# ------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# ------------------------------------------------------------------

def generate_otp():
    """Generate a cryptographically secure 6-digit OTP using `secrets`."""
    return "".join(secrets.choice("0123456789") for _ in range(6))


def send_telegram_otp(otp):
    """Send the OTP to the configured Telegram chat via the Bot API (OOB delivery)."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = (
        f"*Project MFA*\n"
        f"Verification code: `{otp}`\n"
        f"Expires in {OTP_EXPIRY_SECONDS // 60} minutes · do not share this code"
    )
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, data=payload, timeout=10)
    return response.ok


# ------------------------------------------------------------------
# 3. ROUTES (identical logic to the local version)
# ------------------------------------------------------------------

@app.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if USERS.get(username) != password:
        return render_template("login.html", error="Invalid username or password.")

    otp = generate_otp()
    expires_at = time.time() + OTP_EXPIRY_SECONDS
    active_otps[username] = {"otp": otp, "expires_at": expires_at}

    sent = send_telegram_otp(otp)
    if not sent:
        return render_template(
            "login.html",
            error="Could not send OTP via Telegram. Check BOT_TOKEN / CHAT_ID secrets.",
        )

    session["pending_user"] = username
    return redirect(url_for("otp_page"))


@app.route("/otp", methods=["GET"])
def otp_page():
    if "pending_user" not in session:
        return redirect(url_for("login_page"))
    return render_template("otp.html", expiry_seconds=OTP_EXPIRY_SECONDS)


@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    username = session.get("pending_user")
    if not username:
        return redirect(url_for("login_page"))

    submitted_otp = request.form.get("otp", "").strip()
    record = active_otps.get(username)

    if not record:
        return render_template("otp.html", error="No active OTP. Please log in again.",
                                expiry_seconds=OTP_EXPIRY_SECONDS)

    if time.time() > record["expires_at"]:
        del active_otps[username]
        return render_template("otp.html", error="OTP expired. Please log in again.",
                                expiry_seconds=OTP_EXPIRY_SECONDS)

    if submitted_otp != record["otp"]:
        return render_template("otp.html", error="Incorrect OTP. Try again.",
                                expiry_seconds=OTP_EXPIRY_SECONDS)

    del active_otps[username]  # replay attack prevention
    session.pop("pending_user", None)
    session["authenticated_user"] = username
    return redirect(url_for("success_page"))


@app.route("/success", methods=["GET"])
def success_page():
    username = session.get("authenticated_user")
    if not username:
        return redirect(url_for("login_page"))
    return render_template("success.html", username=username)


@app.route("/about", methods=["GET"])
def about_page():
    return render_template("about.html")


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ------------------------------------------------------------------
# 4. CLOUDFLARE WORKERS ENTRYPOINT
# ------------------------------------------------------------------

Default = wsgi.entrypoint(app)
