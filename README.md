# Project MFA

A hands-on demonstration of **Two-Factor Authentication (2FA)** using an **Out-of-Band (OOB)** delivery channel — the Telegram Bot API — built as a security lab for Diploma in Computer Technology (Big Data), TVET MARA Lumut.

Instead of relying on a password alone, this system sends a time-limited, cryptographically secure one-time code to the user's Telegram account. Even if a password is phished, the attacker still needs access to the user's Telegram to log in.

## Features

- 🔐 Cryptographically secure 6-digit OTP generation (Python's `secrets` module)
- 📱 Out-of-Band OTP delivery via the Telegram Bot API
- ⏱ 3-minute OTP expiry
- 🔁 Replay-attack prevention — OTP is deleted immediately after use
- 🎨 Clean, modern 3-step UI (Login → Verify → Done)

## Screenshots

### Website

![Website screenshot](screenshots/website.png)

### Telegram OTP delivery

![Telegram OTP screenshot](screenshots/telegram.png)

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **OOB Channel:** Telegram Bot API
- **Deployment:** Cloudflare Workers (Python Workers / WSGI)

## Project Structure
