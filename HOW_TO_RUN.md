# UCSP — How to Run

## Step 1: Extract ZIP
Extract the ZIP → you get a folder called `ucsp`

## Step 2: Install XAMPP
Download from https://www.apachefriends.org
- Open XAMPP Control Panel
- Click START next to **Apache**
- Click START next to **MySQL**

## Step 3: Setup Database
- Open browser → go to http://localhost/phpmyadmin
- Click **New** (left side)
- Database name: `ucsp_db` → Click **Create**
- Click on `ucsp_db` → Click **Import** tab
- Click **Choose File** → select `database.sql` from the ucsp folder
- Click **Go** at the bottom

## Step 4: Open in VS Code
- Open VS Code
- File → Open Folder → select the `ucsp` folder
- Open Terminal (Ctrl + `)

## Step 5: Install Python packages
```
pip install Flask Flask-MySQLdb mysqlclient
```
If mysqlclient gives error, use:
```
pip install Flask Flask-MySQLdb PyMySQL
```

## Step 6: Run
```
python app.py
```

## Step 7: Open Browser
Go to: http://localhost:5000

## Login Credentials
- Admin: username = admin, password = admin123
- Admin: username = principal, password = prin2026
- Faculty: Add from Admin panel first, then login
- Student: Add from Faculty panel first, then login
