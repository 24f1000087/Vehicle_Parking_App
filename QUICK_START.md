# 🚀 Quick Start Guide - Vehicle Parking App

## For Beginners - Step by Step

### Step 1: Install Docker Desktop
1. Download from: https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Wait until Docker Desktop shows "Docker is running" in the system tray

### Step 2: Start Redis with Docker

Open **Terminal 1** (Command Prompt, PowerShell, or Terminal) and run:

```bash
docker run -d -p 6379:6379 --name redis-parking redis:latest
```

**Verify it's running:**
```bash
docker ps
```

You should see a container named "redis-parking" in the list.

**Test Redis connection (recommended):**
```bash
cd backend
python test_redis.py
```

You should see: `✅ SUCCESS: Redis is running and accessible!`

✅ **Redis is now running!** You can minimize this terminal.

---

### Step 3: Setup Backend

Open **Terminal 2** and navigate to the backend folder:

```bash
cd backend
```

**Create virtual environment (recommended):**
```bash
python -m venv venv
```

**Activate virtual environment:**
```bash
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

---

### Step 4: Start Celery Worker

Keep **Terminal 2** open, or open a **NEW Terminal 3**:

```bash
cd backend
venv\Scripts\activate  # Windows (or source venv/bin/activate on Mac/Linux)
celery -A app.celery worker --loglevel=info
```

**What you should see:**
```
celery@your-computer v5.3.4
[INFO/MainProcess] Connected to redis://localhost:6379/0
[INFO/MainProcess] celery@your-computer ready.
```

✅ **Celery Worker is running!** Keep this terminal open.

---

### Step 5: Start Celery Beat

Open **Terminal 4** (NEW terminal):

```bash
cd backend
venv\Scripts\activate  # Windows (or source venv/bin/activate on Mac/Linux)
celery -A app.celery beat --loglevel=info
```

**What you should see:**
```
celery beat v5.3.4 is starting.
```

✅ **Celery Beat is running!** Keep this terminal open.

---

### Step 6: Start Flask Backend

Open **Terminal 5** (NEW terminal):

```bash
cd backend
venv\Scripts\activate  # Windows (or source venv/bin/activate on Mac/Linux)
flask run
```

**What you should see:**
```
 * Running on http://127.0.0.1:5000
```

✅ **Backend is running!** Keep this terminal open.

---

### Step 7: Start Frontend

Open **Terminal 6** (NEW terminal):

```bash
cd frontend
python -m http.server 8080
```

**What you should see:**
```
Serving HTTP on 0.0.0.0 port 8080
```

✅ **Frontend is running!**

---

### Step 8: Open the App

1. Open your web browser
2. Go to: `http://localhost:8080`
3. You should see the login page!

**Default Admin Login:**
- Username: `admin`
- Password: `admin123`

---

## 📋 Summary - What Should Be Running

You should have **6 terminals/windows** open:

| Terminal | Service | Status |
|----------|---------|--------|
| 1 | Redis (Docker) | ✅ Running in background |
| 2 | Celery Worker | ✅ Keep open |
| 3 | Celery Beat | ✅ Keep open |
| 4 | Flask Backend | ✅ Keep open |
| 5 | Frontend Server | ✅ Keep open |
| 6 | (Optional) Your browser | ✅ http://localhost:8080 |

---

## 🛑 How to Stop Everything

**Stop Redis:**
```bash
docker stop redis-parking
```

**Stop other services:**
- Press `Ctrl + C` in each terminal (Celery Worker, Celery Beat, Flask, Frontend)

**Start Redis again later:**
```bash
docker start redis-parking
```

---

## ❓ Common Issues

### "docker: command not found"
- Install Docker Desktop first
- Make sure Docker Desktop is running

### "Connection refused" when starting Celery
- Redis might not be running
- Check with: `docker ps`
- Start Redis: `docker start redis-parking`

### "No module named 'celery'"
- Make sure you activated virtual environment
- Run: `pip install -r requirements.txt`

### Port 5000 or 8080 already in use
- Close other applications using those ports
- Or change ports in the commands

---

## 🎉 You're All Set!

The app should now be running. Try logging in as admin and creating a parking lot!

For more details, see the main [README.md](README.md) file.

