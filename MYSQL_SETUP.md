# 🗄️ MySQL Database Setup Guide

## Quick Setup

### Step 1: Install MySQL Connector

```bash
pip install pymysql
# OR
pip install mysql-connector-python
```

### Step 2: Configure Connection

Run the setup script:
```bash
python setup_mysql.py
```

Or create a `.env` file manually:
```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_screener
DB_USER=root
DB_PASSWORD=your_password
```

### Step 3: Verify Database Exists

Make sure your MySQL database `ai_screener` exists:

```sql
CREATE DATABASE IF NOT EXISTS ai_screener CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 4: Start the API Server

```bash
python api_server.py
```

The tables will be created automatically on first run!

## What I Need From You

To connect to your MySQL database, I need:

1. **MySQL Host** (usually `localhost`)
2. **MySQL Port** (usually `3306`)
3. **MySQL Username** (e.g., `root`)
4. **MySQL Password**
5. **Database Name**: `ai_screener` (you've already created this)

## Configuration Options

### Option 1: Environment Variables (Recommended)

Create a `.env` file in the project root:

```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_screener
DB_USER=your_username
DB_PASSWORD=your_password
```

### Option 2: Direct Configuration

Edit `config/db_config.py` and update `MYSQL_CONFIG`:

```python
MYSQL_CONFIG: Dict[str, Any] = {
    'host': 'localhost',
    'port': 3306,
    'database': 'ai_screener',
    'user': 'your_username',
    'password': 'your_password',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
}
```

## Tables Created Automatically

The following tables will be created automatically:

- `signals` - Trading signals
- `portfolio` - Portfolio positions
- `trades` - Trade history
- `user_config` - User configuration

## Testing Connection

Test your MySQL connection:

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()
if db.test_connection():
    print("✅ MySQL connection successful!")
else:
    print("❌ Connection failed. Check your credentials.")
```

## Troubleshooting

### "MySQL connector not installed"
```bash
pip install pymysql
```

### "Access denied"
- Check username and password
- Verify user has access to `ai_screener` database
- Grant permissions: `GRANT ALL ON ai_screener.* TO 'your_user'@'localhost';`

### "Can't connect to MySQL server"
- Check if MySQL server is running
- Verify host and port are correct
- Check firewall settings

## Next Steps

Once MySQL is configured:

1. ✅ Tables will be created automatically
2. ✅ Default config will be inserted
3. ✅ API server will connect to MySQL
4. ✅ All data will be stored in MySQL

**Ready to go!** 🚀

