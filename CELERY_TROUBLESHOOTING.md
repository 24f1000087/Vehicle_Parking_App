# 🔧 Celery Troubleshooting Guide

## Common Celery Worker Errors and Solutions

### Error 1: "No module named 'app'"

**Error Message:**
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
1. Make sure you're in the `backend` directory:
   ```bash
   cd backend
   ```

2. Check that `app.py` exists in the current directory:
   ```bash
   dir app.py  # Windows
   ls app.py   # Mac/Linux
   ```

3. Try using Python module syntax:
   ```bash
   python -m celery -A app.celery worker --loglevel=info
   ```

---

### Error 2: "Cannot connect to Redis"

**Error Message:**
```
[ERROR/MainProcess] consumer: Cannot connect to redis://localhost:6379/0: Error 111 connecting to localhost:6379. Connection refused.
```

**Solution:**
1. **Check if Redis is running:**
   ```bash
   docker ps
   ```
   You should see "redis-parking" container.

2. **If Redis is not running, start it:**
   ```bash
   docker start redis-parking
   ```
   
   Or create it if it doesn't exist:
   ```bash
   docker run -d -p 6379:6379 --name redis-parking redis:latest
   ```

3. **Test Redis connection:**
   ```bash
   cd backend
   python test_redis.py
   ```

---

### Error 3: "AttributeError: module 'app' has no attribute 'celery'"

**Error Message:**
```
AttributeError: module 'app' has no attribute 'celery'
```

**Solution:**
1. Make sure you're running from the `backend` directory
2. Try this command instead:
   ```bash
   celery -A app worker --loglevel=info
   ```
   
   Or:
   ```bash
   python -m celery -A app worker --loglevel=info
   ```

---

### Error 4: "ImportError: cannot import name 'celery' from 'app'"

**Error Message:**
```
ImportError: cannot import name 'celery' from 'app'
```

**Solution:**
1. Check that `app.py` has the celery initialization
2. Make sure you installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Try reinstalling celery:
   ```bash
   pip uninstall celery
   pip install celery==5.3.4
   ```

---

### Error 5: "OSError: [Errno 48] Address already in use"

**Error Message:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
Another Celery worker might already be running. 

1. **Find and stop existing Celery processes:**
   ```bash
   # Windows:
   taskkill /F /IM celery.exe
   
   # Mac/Linux:
   pkill -f celery
   ```

2. **Or use a different port/configuration**

---

### Error 6: "ModuleNotFoundError: No module named 'utils.tasks'"

**Error Message:**
```
ModuleNotFoundError: No module named 'utils.tasks'
```

**Solution:**
1. Make sure you're in the `backend` directory
2. Check that `utils/tasks.py` exists:
   ```bash
   dir utils\tasks.py  # Windows
   ls utils/tasks.py   # Mac/Linux
   ```

3. Make sure `utils/__init__.py` exists (it should be empty)

---

## ✅ Correct Way to Start Celery Worker

**Step 1: Navigate to backend directory**
```bash
cd backend
```

**Step 2: Activate virtual environment (if using one)**
```bash
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

**Step 3: Start Celery Worker**
```bash
celery -A app.celery worker --loglevel=info
```

**Alternative commands to try if above doesn't work:**
```bash
# Option 1: Using Python module
python -m celery -A app.celery worker --loglevel=info

# Option 2: Without .celery
celery -A app worker --loglevel=info

# Option 3: Explicit path
celery --app=app.celery worker --loglevel=info
```

---

## 🔍 Debugging Steps

### Step 1: Verify Your Setup

```bash
# 1. Check you're in the right directory
pwd  # Should show .../backend

# 2. Check app.py exists
ls app.py  # or dir app.py on Windows

# 3. Check Redis is running
docker ps | grep redis

# 4. Test Redis connection
python test_redis.py

# 5. Check Celery is installed
python -c "import celery; print(celery.__version__)"
```

### Step 2: Test Celery Import

```bash
python -c "from app import celery; print('Celery imported successfully')"
```

If this fails, there's an issue with your app.py file.

### Step 3: Check for Circular Imports

Make sure your imports in `utils/tasks.py` are correct:
```python
from app import celery  # This should work
```

---

## 📝 Still Having Issues?

1. **Share the full error message** - Copy the entire error from your terminal
2. **Check your current directory** - Run `pwd` (Mac/Linux) or `cd` (Windows)
3. **Verify Redis is running** - Run `docker ps`
4. **Check Python version** - Run `python --version` (should be 3.8+)
5. **Reinstall dependencies** - Run `pip install -r requirements.txt`

---

## 🎯 Quick Fix Checklist

- [ ] Redis is running (`docker ps` shows redis-parking)
- [ ] You're in the `backend` directory
- [ ] Virtual environment is activated (if using one)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `app.py` exists in current directory
- [ ] No other Celery worker is running
- [ ] Python version is 3.8 or higher

