# Resume Bot — PythonAnywhere Webhook Build

This repo is ready to deploy on **PythonAnywhere** using **webhooks** (Flask).
It still supports local dev via polling (`python main.py`).

## Quick start (local)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=xxxx:yyyy
python main.py
```

## Deploy on PythonAnywhere
1) Push this repo to GitHub and clone it in a PythonAnywhere Bash console.
2) Create a venv and install deps:
```bash
cd ~/resume-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3) Web tab → Add new **Flask** app → Python 3.x. Edit the WSGI file to point to this project (see below).
4) Web tab → Environment variables: set `TELEGRAM_BOT_TOKEN`, `WEBHOOK_SECRET`, `PA_USERNAME`.
5) Reload the web app.
6) In Bash (venv activated), run:
```bash
python pa_set_webhook.py
```
7) DM your bot `/start`.

### WSGI snippet (replace <your-username>)
Edit `/var/www/<your-username>_pythonanywhere_com_wsgi.py`:
```python
import sys, os
path = '/home/<your-username>/resume-bot'  # repo folder
if path not in sys.path:
    sys.path.append(path)

activate_this = '/home/<your-username>/resume-bot/.venv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

from pa_web import application
```

### Notes
- Free PA plan may block outbound to `api.telegram.org`; paid plan recommended for bots.
- Change `WEBHOOK_SECRET` if you want a new endpoint path, then rerun `pa_set_webhook.py`.
