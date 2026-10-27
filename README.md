# SnapLink — URL Shortener

A fast, beautiful URL shortener built with **Django** featuring real-time analytics, QR code generation, and a modern dark UI.

## Features

- ⚡ **Instant URL Shortening** — AJAX-powered, no page reload
- 🏷️ **Custom Aliases** — Branded short links (e.g. `/my-campaign`)
- 📊 **Analytics Dashboard** — Click tracking with Chart.js visualizations
- 📱 **QR Code Generator** — Download PNG QR codes for every link
- ⏰ **Link Expiration** — Set per-link expiry date/time
- 🔍 **Search & Filter** — Live search across all your links
- 🖥️ **Device Tracking** — Desktop / Mobile / Tablet per click
- 🛡️ **Django Admin** — Full admin panel

## Tech Stack

- **Backend:** Django 6.x (Python 3.13)
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Frontend:** Vanilla HTML/CSS/JS — dark glassmorphism design
- **Libraries:** `qrcode`, `Pillow`, `Chart.js`

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/Iam-Rohan-raj/fds-project.git
cd fds-project

# 2. Install dependencies
pip install django qrcode pillow

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Start the server
python manage.py runserver
```

Visit **http://127.0.0.1:8000** to get started.

## Admin

Go to **http://127.0.0.1:8000/admin/** and log in with your superuser credentials.

## Screenshots

| Homepage | Analytics |
|----------|-----------|
| Dark hero with shortener form | Click charts & device breakdown |

## License

MIT
