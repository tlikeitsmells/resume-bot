# Resume Bot

A Telegram bot that helps you build an ATS-friendly résumé interactively:
- Collects contact, skills, experience, and education.
- Helps you write measurable bullet points.
- Tailors bullets to a pasted job description.
- Exports clean `.docx` and `.txt` versions.

---

## 🚀 Setup

### 1. Clone this repo
```bash
git clone https://github.com/<your-username>/resume-bot.git
cd resume-bot
```

### 2. Create a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your bot token
Create a bot with **@BotFather** on Telegram, copy the token, then:
```bash
export TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11   # Mac/Linux
setx TELEGRAM_BOT_TOKEN "123456:ABC-DEF..."                          # Windows
```

### 5. Run the bot
```bash
python main.py
```

---

## 🛠️ Usage
In Telegram DM with your bot:

- `/contact` → enter name, email, phone, etc.
- `/experience` → add roles & bullets (with `/done` to finish a job)
- `/skills` → add core skills, tools, certs
- `/education` → add education
- `/summary` → add your professional summary
- `/tailor` → paste a job description, get bullet suggestions
- `/export` → get `resume.docx` and `resume.txt`

---

## 📌 Next Features
- Multiple résumé templates
- LinkedIn import (PDF → parsed)
- Named résumé variants
