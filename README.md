# alx-backend-security

A Django project focused on **security best practices**, including request logging, IP blacklisting, geolocation analytics, rate limiting, and anomaly detection using Celery.

---

## Features

### Task 0: Basic IP Logging Middleware
- Logs every request's:
  - IP address
  - Timestamp
  - Path
- Saves logs in `RequestLog` model.

### Task 1: IP Blacklisting
- Block requests from blacklisted IPs using `BlockedIP` model.
- Middleware returns **403 Forbidden** for blocked IPs.
- Includes Django management command `block_ip` to add IPs.

### Task 2: IP Geolocation Analytics
- Enhances logs with **country** and **city** using [`django-ip-geolocation`](https://pypi.org/project/django-ip-geolocation/).
- Geolocation results are cached for 24 hours.

### Task 3: Rate Limiting by IP
- Uses [`django-ratelimit`](https://pypi.org/project/django-ratelimit/).
- Configured limits:
  - **Authenticated users** → 10 requests/minute
  - **Anonymous users** → 5 requests/minute
- Applied to sensitive views like `login`.

### Task 4: Anomaly Detection
- **Celery periodic task** runs hourly:
  - Flags IPs making **>100 requests/hour**.
  - Flags IPs accessing sensitive paths (`/admin`, `/login`).
- Stores results in `SuspiciousIP` model.

---