// PM2 Configuration for AI Screener
// This manages the Python/Streamlit application

module.exports = {
  apps: [{
    name: 'ai-screener-streamlit',
    script: 'venv/bin/streamlit',
    args: 'run enhanced_screener.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection true',
    cwd: '/var/www/ai-screener',
    interpreter: 'none',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PYTHONUNBUFFERED: '1',
      STREAMLIT_SERVER_HEADLESS: 'true'
    },
    error_file: './logs/error.log',
    out_file: './logs/output.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    min_uptime: '10s',
    max_restarts: 10
  }]
};

