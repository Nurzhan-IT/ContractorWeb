# Gunicorn configuration for ContractorWebDev
# Docs: https://docs.gunicorn.org/en/stable/settings.html

import multiprocessing

# Bind to Unix socket (nginx will proxy to this)
bind = "unix:/run/contractorwebdev/gunicorn.sock"

# Workers: 2–4 × CPU cores is the standard recommendation
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class: sync is fine for this app (no async I/O needed)
worker_class = "sync"

# Timeout: 120s for AI calls (OpenRouter can be slow)
timeout = 120

# Graceful restart timeout
graceful_timeout = 30

# Keep-alive
keepalive = 5

# Log to stdout/stderr (systemd captures these)
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process name (shows in `ps aux`)
proc_name = "contractorwebdev"

# Preload app for faster worker startup and memory sharing
preload_app = True

# Reload on code changes (disable in prod, enable for staging)
reload = False
