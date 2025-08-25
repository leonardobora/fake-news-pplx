# Fake News Detection Flask App - Deployment Configuration

## Gunicorn Configuration
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True
user = None
group = None
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

## Environment Variables for Production
# PERPLEXITY_API_KEY=your_actual_api_key
# SECRET_KEY=your_secret_key_here
# FLASK_ENV=production

## Nginx Configuration (example)
# server {
#     listen 80;
#     server_name your-domain.com;
#     
#     location / {
#         proxy_pass http://127.0.0.1:5000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#     }
# }

## Docker Configuration (example)
# FROM python:3.11-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# EXPOSE 5000
# CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]

## Systemd Service (example)
# [Unit]
# Description=Fake News Detection Flask App
# After=network.target
# 
# [Service]
# User=www-data
# Group=www-data
# WorkingDirectory=/path/to/app
# Environment=PATH=/path/to/venv/bin
# ExecStart=/path/to/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
# Restart=always
# 
# [Install]
# WantedBy=multi-user.target