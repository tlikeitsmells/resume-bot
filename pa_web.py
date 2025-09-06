import os
from flask import Flask, request, abort
from telegram import Update
from main import build_application

app = Flask(__name__)
application = app  # PythonAnywhere expects 'application'

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "set-a-secret-path")

ptb_app = build_application()
bot = ptb_app.bot

@app.post(f"/{WEBHOOK_SECRET}")
def telegram_webhook():
    if request.headers.get("Content-Type") != "application/json":
        return abort(415)
    update = Update.de_json(request.get_json(force=True), bot)
    ptb_app.create_task(ptb_app.process_update(update))
    return "ok"
