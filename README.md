# Vehicle Parking App - V2

A complete full-stack vehicle parking management application with admin and user roles.

## 📁 Project Structure

```
Vehicle_parking_app_24f1000087/
├── frontend/
│   ├── src/
│   │   ├── app.js (all Vue components defined here)
│   │   └── components/ (original .vue files kept for reference)
│   │       ├── Login.vue
│   │       ├── AdminDashboard.vue
│   │       ├── UserDashboard.vue
│   │       ├── ParkingLotView.vue
│   │       ├── ReservationView.vue
│   │       └── ChartsView.vue
│   ├── index.html
│   └── package.json
└── backend/
    ├── app.py
    ├── routes/
    │   ├── auth_routes.py
    │   ├── admin_routes.py
    │   └── user_routes.py
    ├── models/
    │   ├── user_model.py
    │   ├── parkinglot_model.py
    │   ├── parkingspot_model.py
    │   ├── reservation_model.py
    │   └── __init__.py
    ├── utils/
    │   ├── cache.py
    │   ├── tasks.py
    │   ├── mailer.py
    │   └── __init__.py
    └── requirements.txt
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- Docker Desktop (for running Redis)
- Node.js (optional, for npm)
- Gmail account (for email functionality - optional)

### Backend Setup

1. **Navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended):**

   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start Redis using Docker (Recommended for beginners):**

   **Option A: Using Docker (Easiest)**

   Make sure Docker Desktop is running, then open a terminal and run:

   ```bash
   docker run -d -p 6379:6379 --name redis-parking redis:latest
   ```

   This command:

   - `-d` = runs in background (detached mode)
   - `-p 6379:6379` = maps port 6379 (Redis default port)
   - `--name redis-parking` = gives the container a friendly name
   - `redis:latest` = uses the latest Redis image

   **Verify Redis is running:**

   ```bash
   docker ps
   ```

   You should see a container named "redis-parking" running.

   **Test Redis connection (optional but recommended):**

   ```bash
   cd backend
   python test_redis.py
   ```

   This will verify Redis is working correctly.

   **To stop Redis later:**

   ```bash
   docker stop redis-parking
   ```

   **To start Redis again:**

   ```bash
   docker start redis-parking
   ```

   **Option B: Install Redis locally (Advanced)**

   If you prefer not to use Docker, install Redis directly:

   - Windows: Download from https://github.com/microsoftarchive/redis/releases
   - Linux: `sudo apt-get install redis-server` (Ubuntu/Debian)
   - Mac: `brew install redis`

   Then run: `redis-server`

5. **Start Celery Worker (Open a NEW terminal window):**

   **Important:** Keep this terminal open! The worker needs to keep running.

   ```bash
   # Navigate to backend folder
   cd backend

   # Activate virtual environment (if using one)
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate

   # Start Celery worker
   celery -A app.celery worker --loglevel=info
   ```

   You should see output like:

   ```
   celery@your-computer v5.3.4 (emerald-rush)
   ...
   [INFO/MainProcess] Connected to redis://localhost:6379/0
   [INFO/MainProcess] celery@your-computer ready.
   ```

   ✅ **Success!** The worker is now running and waiting for tasks.

6. **Start Celery Beat for Scheduled Tasks (Open ANOTHER NEW terminal window):**

   **Important:** Keep this terminal open too! Beat schedules periodic tasks.

   ```bash
   # Navigate to backend folder
   cd backend

   # Activate virtual environment (if using one)
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate

   # Start Celery beat
   celery -A app.celery beat --loglevel=info
   ```

   You should see output like:

   ```
   celery beat v5.3.4 (emerald-rush) is starting.
   ...
   [INFO] Scheduler: Sending due task utils.tasks.send_daily_reminders
   ```

   ✅ **Success!** Celery beat is now scheduling tasks.

7. **Run Flask Backend (Open a THIRD terminal window):**

   ```bash
   # Navigate to backend folder
   cd backend

   # Activate virtual environment (if using one)
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate

   # Run Flask
   flask run
   # Or: python app.py
   ```

   You should see:

   ```
   * Running on http://127.0.0.1:5000
   ```

   ✅ **Success!** Backend is running on `http://localhost:5000`

**Summary - You need 4 terminals/windows open:**

1. ✅ Terminal 1: Redis (Docker) - `docker run -d -p 6379:6379 --name redis-parking redis:latest`
2. ✅ Terminal 2: Celery Worker - `celery -A app.celery worker --loglevel=info`
3. ✅ Terminal 3: Celery Beat - `celery -A app.celery beat --loglevel=info`
4. ✅ Terminal 4: Flask Backend - `flask run`

### Frontend Setup

1. **Navigate to frontend directory:**

   ```bash
   cd frontend
   ```

2. **Start development server:**

   ```bash
   # Using Python's built-in server:
   python -m http.server 8080

   # Or using Node.js http-server (if installed):
   npx http-server -p 8080
   ```

   Frontend will run on `http://localhost:8080`

3. **Open browser:**
   Navigate to `http://localhost:8080`

   **Note:** The frontend uses Vue 3 via CDN (no build step required). All components are defined in `src/app.js` as JavaScript objects for CDN compatibility.

---

Any console errors
What you see when opening http://localhost:5000/api/health
What the test page shows at http://localhost:8080/test.html

## 🔐 Default Credentials

- **Admin:**

  - Username: `admin`
  - Password: `admin123`

- **User:**
  - Register a new account through the registration form

## 📋 Features

### Admin Features

- Create, update, delete parking lots
- View all users
- View parking spot statuses
- View summary statistics
- View analytics charts (daily reservations, revenue, lot occupancy)

### User Features

- Register and login
- View available parking lots
- Book parking spots (auto-allocation)
- Vacate parking spots
- View reservation history
- Export reservations as CSV

## 🔧 Configuration

### Email Configuration (Optional)

Edit `backend/app.py` to configure email settings:

```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'  # Gmail app password
```

### Redis Configuration

Default Redis URL: `redis://localhost:6379/0`

You can change it via environment variable:

```bash
export REDIS_URL=redis://localhost:6379/0
```

## 🗄️ Database

- SQLite database is automatically created at `backend/parking_app.db`
- Default admin user is automatically created on first run
- All tables are created automatically

## 📡 API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user

### Admin Routes

- `GET /api/admin/parking-lots` - Get all parking lots
- `POST /api/admin/parking-lots` - Create parking lot
- `PUT /api/admin/parking-lots/<id>` - Update parking lot
- `DELETE /api/admin/parking-lots/<id>` - Delete parking lot
- `GET /api/admin/users` - Get all users
- `GET /api/admin/spots/<lot_id>` - Get spots for a lot
- `GET /api/admin/summary` - Get summary statistics
- `GET /api/admin/charts` - Get chart data

### User Routes

- `GET /api/user/parking-lots` - Get available parking lots
- `POST /api/user/book` - Book a parking spot
- `POST /api/user/vacate` - Vacate current spot
- `GET /api/user/reservations` - Get user reservations
- `GET /api/user/reservations/active` - Get active reservation
- `GET /api/user/export-csv-sync` - Export CSV (synchronous)

## 🧪 Testing

1. **Start all services:**

   - Redis server
   - Celery worker
   - Celery beat
   - Flask backend
   - Frontend server

2. **Test login:**

   - Use admin credentials: `admin` / `admin123`
   - Or register a new user

3. **Test admin features:**

   - Create a parking lot
   - View users
   - Check charts

4. **Test user features:**
   - Book a spot
   - View reservations
   - Export CSV

## 📝 Notes

- Redis is required for caching and Celery (use Docker for easy setup)
- Celery tasks run in background (daily reminders, monthly reports)
- Email functionality requires Gmail SMTP configuration
- Database is SQLite (auto-created)
- JWT tokens are used for authentication
- All routes are protected with JWT authentication

## 📚 Additional Resources

- **Quick Start Guide:** See [QUICK_START.md](QUICK_START.md) for step-by-step beginner instructions
- **Docker Redis:** Make sure Docker Desktop is running before starting Redis
- **Multiple Terminals:** You need 4-5 terminal windows open simultaneously

## 🐛 Troubleshooting

### Redis Issues

1. **"Connection refused" or "Cannot connect to Redis" error:**

   **Check if Redis container is running:**

   ```bash
   docker ps
   ```

   If you don't see "redis-parking", start it:

   ```bash
   docker start redis-parking
   ```

   If the container doesn't exist, create it:

   ```bash
   docker run -d -p 6379:6379 --name redis-parking redis:latest
   ```

   **Check if port 6379 is already in use:**

   ```bash
   # Windows PowerShell:
   netstat -ano | findstr :6379

   # Linux/Mac:
   lsof -i :6379
   ```

   If something else is using port 6379, stop it or use a different port.

2. **Docker command not found:**
   - Make sure Docker Desktop is installed and running
   - Download from: https://www.docker.com/products/docker-desktop

### Celery Issues

3. **"No module named 'celery'" error:**

   ```bash
   pip install celery
   # Or reinstall all dependencies:
   pip install -r requirements.txt
   ```

4. **Celery worker won't connect to Redis:**

   - Make sure Redis is running (see Redis Issues above)
   - Check that you're in the `backend` directory when running Celery
   - Verify Redis URL in `backend/app.py` is `redis://localhost:6379/0`

5. **Celery worker shows "Connection refused":**

   - Redis might not be running - start it with Docker
   - Check firewall settings aren't blocking port 6379

6. **"No such file or directory: app.celery" error:**
   - Make sure you're in the `backend` directory
   - Check that `app.py` exists in the current directory
   - Try: `cd backend` then run the celery command again

### General Issues

7. **Database errors:**

   - Delete `backend/parking_app.db` and restart Flask to recreate

8. **CORS errors:**

   - Make sure backend CORS is enabled (it is by default)
   - Check frontend API URL in `frontend/src/app.js` is `http://localhost:5000/api`

9. **Import errors:**

   - Make sure you're in the correct directory
   - Check Python path and virtual environment is activated
   - Try: `pip install -r requirements.txt` again

10. **Port already in use (Flask):**
    - Another app might be using port 5000
    - Change Flask port: `flask run --port 5001`
    - Update frontend API URL accordingly

## 📄 License

MIT License

## 👨‍💻 Author

Vehicle Parking App - V2
