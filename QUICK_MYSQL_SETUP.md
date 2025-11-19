# ⚡ Quick MySQL Setup (You Already Have MySQL!)

Since you already have MySQL installed, here's the quickest way to connect:

## Step 1: Install MySQL Connector

```bash
.\venv\Scripts\Activate.ps1
pip install pymysql
```

## Step 2: Configure Connection

**Option A: Create .env file (Recommended)**

Create a `.env` file in the project root (`C:\python\ai-screener\.env`):

```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_screener
DB_USER=root
DB_PASSWORD=your_mysql_password
```

**Option B: Edit config directly**

Edit `config/db_config.py` and update:

```python
MYSQL_CONFIG: Dict[str, Any] = {
    'host': 'localhost',        # Your MySQL host
    'port': 3306,                # Your MySQL port
    'database': 'ai_screener',   # Your database name
    'user': 'root',              # Your MySQL username
    'password': 'your_password', # Your MySQL password
    ...
}
```

## Step 3: Test Connection

```bash
python test_mysql_connection.py
```

This will:
- ✅ Test the connection
- ✅ Create tables automatically if needed
- ✅ Show any errors

## Step 4: Start API Server

```bash
python api_server.py
```

The tables will be created automatically on first run!

## What Tables Will Be Created?

- `signals` - Trading signals
- `portfolio` - Portfolio positions  
- `trades` - Trade history
- `user_config` - User configuration

All tables use UTF8MB4 charset for full Unicode support.

## Need Help?

If connection fails:
1. Check MySQL is running: `mysql -u root -p`
2. Verify database exists: `SHOW DATABASES;`
3. Check user permissions
4. Review error messages in test script

**That's it! You're ready to go!** 🚀

