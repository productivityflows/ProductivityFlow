# Gunicorn configuration file for Railway deployment
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"

# Worker processes - Railway optimized
workers = 1  # Single worker for reliability
worker_class = "sync"
timeout = 30  # Reduced timeout for Railway
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Don't preload application
preload_app = False

# Logging
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "productivityflow-backend"

# Daemonize the Gunicorn process (detach & enter background)
daemon = False