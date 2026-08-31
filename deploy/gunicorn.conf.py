# Gunicorn configuration for ContractorWebDev
# Docs: https://docs.gunicorn.org/en/stable/settings.html

import multiprocessing

# Bind to Unix socket (nginx will proxy to this)
bind = 'unix:/run/contractorwebdev/gunicorn.sock'

# Workers: with gthread, fewer workers + more threads is optimal
workers = multiprocessing.cpu_count() * 2 + 1

# gthread: each worker runs N threads concurrently.
# While one thread waits for OpenRouter API, others serve normal requests.
worker_class = 'gthread'
threads = 4  # each worker handles up to 4 concurrent requests

# Timeout: 120s for AI calls (OpenRouter can be slow)
timeout = 120

# Graceful restart timeout
graceful_timeout = 30

# Keep-alive
keepalive = 5

# Log to stdout/stderr (systemd captures these)
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process name (shows in `ps aux`)
proc_name = 'contractorwebdev'

# Preload app for faster worker startup and memory sharing
preload_app = True

# Reload on code changes (disable in prod, enable for staging)
reload = False
