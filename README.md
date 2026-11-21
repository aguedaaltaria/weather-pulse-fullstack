# ☀️ WeatherPulse Studio — Full-Stack Weather & AI Advisory App

**Author:** Águeda Arelis Guzmán Durán  
**Assessment Completed:** **Tech Assessment #1 (Frontend) & Tech Assessment #2 (Backend) — Full Stack**

WeatherPulse Studio is a full-stack, bilingual (**EN/ES**) weather application built with **Vue 3 + Vite** (pure CSS Claymorphism UI) and a **Python Flask + SQLite** RESTful API. It combines real-time weather forecasting, browser geolocation, interactive mapping, full CRUD persistence with strict validations, multi-format data export, and **Google Gemini AI** weather tips.

---

## ✨ Key Features

### Assessment #1 — Frontend (Vue 3 + Vite, Pure CSS)
- **Flexible Location Search:** Supports city/town names, ZIP/postal codes, landmarks, and GPS coordinates (`lat, lon`).
- **Browser Geolocation:** One-click **"My Location"** button using the browser's Geolocation API + reverse geocoding.
- **Current Weather & Detailed Metrics:** Live temperature, "feels like", humidity, wind speed, weather condition icons, and visual progress bars.
- **5-Day Forecast & Weekly Curve:** Organized daily forecast rows with min/max temperature bars plus a CSS-powered vertical bar chart.
- **Unit & Language Toggles:** Instant switching between **Metric (`°C`, `km/h`)** and **Imperial (`°F`, `mph`)**, and full **English / Spanish** support.
- **Graceful Error Handling:** Descriptive error banners for invalid locations, denied GPS permissions, or upstream API timeouts.
- **Identity & PMA Info:** Author credit in the header and an **Info** modal featuring Product Manager Accelerator's mission.

### Assessment #2 — Backend (Flask + SQLite RESTful API)
- **Full CRUD Persistence (`SQLite`):**
  - **CREATE (`POST /api/records`):** Validates location existence and date ranges (`start_date <= end_date`), fetches real historical/forecast temperatures from Open-Meteo, and stores records in SQLite.
  - **READ (`GET /api/records`):** Lists all saved weather queries with resolved location names, date ranges, average temperatures, and notes.
  - **UPDATE (`PUT /api/records/<id>`):** Allows editing location, date range, and notes with the same server-side validations and automatic temperature refresh.
  - **DELETE (`DELETE /api/records/<id>`):** Permanently removes a saved record by ID.
- **Multi-Format Data Export (`GET /api/export/<format>`):** Download all saved records in **JSON**, **CSV**, **Markdown (`.md`)**, or **PDF**.
- **Bonus API Integrations:**
  - **Interactive Map:** Leaflet + OpenStreetMap showing the exact resolved coordinates with a dynamic marker.
  - **AI Weather Advisor:** Google Gemini API (`gemini-2.5-flash-lite` / fallback) generating concise, contextual weather tips in English or Spanish.

---

## 📱 Responsive Design Techniques Used
- **CSS Grid (`repeat(auto-fit, minmax(...))`):** Automatically reflows CRUD forms and metric grids across desktop, tablet, and mobile viewports.
- **Flexbox (`flex-wrap: wrap`):** Keeps header controls, search bars, and forecast rows aligned without horizontal overflow.
- **CSS Media Queries (`@media`):** Adjusts the main two-column dashboard layout (`max-width: 760px`) and collapses the 4-tab navigation bar into a 2x2 grid on small screens (`max-width: 640px`).

---

## 🛠️ Tech Stack
- **Frontend:** Vue 3, Vite, Vanilla CSS (Claymorphism / *Terracotta Sky* theme), Leaflet.js
- **Backend:** Python 3.13, Flask, Flask-CORS, SQLite, `uv`, Requests, FPDF2, Google GenAI SDK
- **External APIs:** Open-Meteo (Forecast & Historical), OpenStreetMap Nominatim (Geocoding & Reverse Geocoding), Google Gemini API

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone [https://github.com/aguedaaltaria/weather-pulse-fullstack.git](https://github.com/aguedaaltaria/weather-pulse-fullstack.git)
cd weather-pulse-fullstack
