# Project MFA

A lightweight implementation of **Two-Factor Authentication (2FA)** using an **Out-of-Band (OOB)** delivery channel via the Telegram Bot API, deployed on Cloudflare Python Workers.

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
