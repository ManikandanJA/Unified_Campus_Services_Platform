# UCSP — Unified Campus Services Platform

## Stack
- Frontend: HTML, CSS, JS, Bootstrap icons
- Backend: Python Flask
- Database: MySQL

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup MySQL
Open MySQL and run:
```sql
source database.sql
```
Or import via phpMyAdmin.

### 3. Update config.py
```python
MYSQL_PASSWORD = 'your_mysql_password'
```

### 4. Run
```bash
python app.py
```

Open browser: http://localhost:5000

## Default Login
- Admin: `admin` / `admin123`
- Admin: `principal` / `prin2026`
- Faculty: Add via Admin panel, then login
- Student: Add via Faculty panel, then login

## Features
- Admin: Manage Faculty, Students, Bus Routes, Events, Placed, Rank Holders, Ticker Updates
- Faculty: Login, view students (dept filtered)
- Student: Login, view events/bus/placed/rank
- Home: Live ticker from DB, placed/rank cards, bus/event preview
