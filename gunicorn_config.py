import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
backlog = 2048

# Worker processes - fewer needed for simple metadata extraction
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Timeout settings
timeout = 30  # 30 seconds is enough for metadata extraction
graceful_timeout = 30
keepalive = 5

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = 'metadata-extraction-api'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Worker temp directory
worker_tmp_dir = "/dev/shm"

# Preload app for better memory usage
preload_app = True
