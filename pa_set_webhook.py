import os
from main import build_application

username = os.environ["PA_USERNAME"]
secret   = os.environ["WEBHOOK_SECRET"]
url = f"https://{username}.pythonanywhere.com/{secret}"

app = build_application()
app.bot.set_webhook(url)
print("Webhook set to:", url)
