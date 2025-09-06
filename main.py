import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters, ContextTypes
from docx import Document
from jinja2 import Template
from storage import Store
from tailoring import job_keywords, score_bullet, suggest_rewrite

ASK_CONTACT, ASK_EXP_ROLE, ASK_EXP_BULLETS, ASK_EDU, ASK_SKILLS, TAILOR_JOB = range(6)
store = Store()

def ats_docx(profile, path="resume_output.docx"):
    doc = Document()
    c = profile["contact"]
    doc.add_heading(c["name"], 0)
    doc.add_paragraph(f"{c['location']} · {c['phone']} · {c['email']}")
    if c.get("links"):
        doc.add_paragraph(" · ".join(c["links"]))
    if profile["summary"]:
        doc.add_heading("Summary", 2)
        doc.add_paragraph(profile["summary"])
    if profile["skills"]["core"] or profile["skills"]["tools"] or profile["skills"]["certs"]:
        doc.add_heading("Skills", 2)
        core = ", ".join(profile["skills"]["core"])
        tools = ", ".join(profile["skills"]["tools"])
        certs = ", ".join(profile["skills"]["certs"])
        doc.add_paragraph("; ".join([s for s in [core, tools, certs] if s]))
    if profile["experience"]:
        doc.add_heading("Experience", 2)
        for r in profile["experience"]:
            h = f"{r['title']} — {r['company']} · {r['location']}  ({r['start']}–{r['end']})"
            doc.add_paragraph(h)
            for b in r["bullets"]:
                doc.add_paragraph(f"• {b}")
    if profile["education"]:
        doc.add_heading("Education", 2)
        for e in profile["education"]:
            p = f"{e['degree']} — {e['school']} · {e['location']} ({e['end']})"
            doc.add_paragraph(p)
            for h in e.get("highlights", []):
                doc.add_paragraph(f"• {h}")
    doc.save(path)
    return path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I’ll build an ATS-friendly résumé with you.\n"
        "Commands:\n"
        "/contact  /experience  /education  /skills  /summary\n"
        "/tailor (paste job description)  /export  /show"
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send your contact line like:\n"
        "Full Name | email | phone | City, ST | links (comma-sep)")
    return ASK_CONTACT

async def contact_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = store.get_profile(update.effective_user.id)
    parts = [s.strip() for s in update.message.text.split("|")]
    try:
        p["contact"]["name"] = parts[0]
        p["contact"]["email"] = parts[1]
        p["contact"]["phone"] = parts[2]
        p["contact"]["location"] = parts[3]
        p["contact"]["links"] = [x.strip() for x in parts[4].split(",")] if len(parts)>4 else []
        store.set_profile(update.effective_user.id, p)
        await update.message.reply_text("Contact saved. Now /experience or /skills?")
        return ConversationHandler.END
    except Exception:
        await update.message.reply_text("Format not recognized. Try again or /cancel.")
        return ASK_CONTACT

async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Role | Company | City, ST | YYYY-MM start | YYYY or Present end")
    return ASK_EXP_ROLE

async def exp_role_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = [s.strip() for s in update.message.text.split("|")]
    if len(parts)<5:
        await update.message.reply_text("Please include all 5 fields.")
        return ASK_EXP_ROLE
    context.user_data["current_role"] = {
        "title":parts[0],"company":parts[1],"location":parts[2],
        "start":parts[3],"end":parts[4],"bullets":[]
    }
    await update.message.reply_text("Great. Send 3–6 bullets (one per message). Type /done when finished.\n"
                                    "Tip: Start with a strong verb and include a metric (%, $, #).")
    return ASK_EXP_BULLETS

async def exp_bullet_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    b = update.message.text.strip()
    if not b or b.startswith("/"): return ASK_EXP_BULLETS
    context.user_data["current_role"]["bullets"].append(b)
    await update.message.reply_text("Added. Another bullet or /done when finished.")
    return ASK_EXP_BULLETS

async def exp_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = store.get_profile(update.effective_user.id)
    p["experience"].insert(0, context.user_data["current_role"])
    store.set_profile(update.effective_user.id, p)
    await update.message.reply_text("Experience saved. Add another /experience, or /skills, /education, /summary, or /export.")
    return ConversationHandler.END

async def summary_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Paste a tight 2–3 line professional summary.")
    return ASK_EDU  # reusing slot for brevity

async def summary_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = store.get_profile(update.effective_user.id)
    p["summary"] = update.message.text.strip()
    store.set_profile(update.effective_user.id, p)
    await update.message.reply_text("Summary saved. /export when ready.")
    return ConversationHandler.END

async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Degree | School | City, ST | Year End (YYYY)")
    return ASK_EDU

async def education_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = [s.strip() for s in update.message.text.split("|")]
    p = store.get_profile(update.effective_user.id)
    p["education"].append({"degree":parts[0], "school":parts[1], "location":parts[2], "end":parts[3], "highlights":[]})
    store.set_profile(update.effective_user.id, p)
    await update.message.reply_text("Education saved. /skills or /export?")
    return ConversationHandler.END

async def skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Core skills (comma-sep)\nTools (comma-sep)\nCerts (comma-sep)\nSend as three lines.")
    return ASK_SKILLS

async def skills_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = update.message.text.splitlines()
    p = store.get_profile(update.effective_user.id)
    p["skills"]["core"]  = [s.strip() for s in lines[0].split(",")] if lines else []
    p["skills"]["tools"] = [s.strip() for s in (lines[1].split(",") if len(lines)>1 else [])]
    p["skills"]["certs"] = [s.strip() for s in (lines[2].split(",") if len(lines)>2 else [])]
    store.set_profile(update.effective_user.id, p)
    await update.message.reply_text("Skills saved. /export when ready.")
    return ConversationHandler.END

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = store.get_profile(update.effective_user.id)
    txt = f"*{p['contact']['name']}*\n{p['summary']}\n\n" \
          f"Skills: {', '.join(p['skills']['core'])}\n" \
          f"Experience roles: {', '.join([r['title'] for r in p['experience']])}"
    await update.message.reply_markdown_v2(txt or "No profile yet. Use /contact to start.")

async def tailor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Paste the job description. I’ll rank and suggest bullet tweaks.")
    return TAILOR_JOB

async def tailor_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jd = update.message.text
    kw = job_keywords(jd)
    p = store.get_profile(update.effective_user.id)
    ranked = []
    for r in p["experience"]:
        for b in r["bullets"]:
            ranked.append((score_bullet(b, kw), b, r["title"]))
    ranked.sort(reverse=True, key=lambda x: x[0])
    top = ranked[:8]
    suggestions = []
    for _, b, t in top:
        suggestions.append(f"• {suggest_rewrite(b, kw)}  _(from {t})_")
    await update.message.reply_markdown("\n".join(suggestions) or "No bullets yet. Add /experience first.")
    return ConversationHandler.END

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = store.get_profile(update.effective_user.id)
    path = ats_docx(p, "resume_output.docx")
    await update.message.reply_document(InputFile(path), filename="resume.docx")
    # Also provide a plain text version for quick pasting
    lines = [p["contact"]["name"], f"{p['contact']['location']} | {p['contact']['phone']} | {p['contact']['email']}"]
    if p["summary"]: lines += ["", "Summary", p["summary"]]
    if p["skills"]["core"] or p["skills"]["tools"] or p["skills"]["certs"]:
        lines += ["", "Skills", ", ".join(p["skills"]["core"] + p["skills"]["tools"] + p["skills"]["certs"])]
    if p["experience"]:
        lines += ["", "Experience"]
        for r in p["experience"]:
            lines += [f"{r['title']} — {r['company']} · {r['location']} ({r['start']}–{r['end']})"]
            lines += [f" - {b}" for b in r["bullets"]]
    if p["education"]:
        lines += ["", "Education"]
        for e in p["education"]:
            lines += [f"{e['degree']} — {e['school']} · {e['location']} ({e['end']})"]
    txt = "\n".join(lines)
    await update.message.reply_document(document=txt.encode("utf-8"), filename="resume.txt")

def conv(handler, msg_handler, state):
    return ConversationHandler(
        entry_points=[CommandHandler(handler.__name__.replace("_cmd",""), handler)],
        states={state: [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler)]},
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)]
    )

def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("contact", contact)],
        states={ASK_CONTACT:[MessageHandler(filters.TEXT & ~filters.COMMAND, contact_capture)]},
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)]
    ))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("experience", experience)],
        states={
            ASK_EXP_ROLE:[MessageHandler(filters.TEXT & ~filters.COMMAND, exp_role_capture)],
            ASK_EXP_BULLETS:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, exp_bullet_add),
                CommandHandler("done", exp_done)
            ]},
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)]
    ))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("education", education)],
        states={ASK_EDU:[MessageHandler(filters.TEXT & ~filters.COMMAND, education_capture)]},
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)]
    ))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("skills", skills)],
        states={ASK_SKILLS:[MessageHandler(filters.TEXT & ~filters.COMMAND, skills_capture)]},
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)]
    ))
    app.add_handler(CommandHandler("summary", summary_cmd))
    app.add_handler(MessageHandler(filters.Regex(r"^(?s).*$") & filters.ChatType.PRIVATE, summary_capture), 1)

    app.add_handler(CommandHandler("show", show))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("tailor", tailor)],
        states={TAILOR_JOB:[MessageHandler(filters.TEXT & ~filters.COMMAND, tailor_capture)]},
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)]
    ))
    app.add_handler(CommandHandler("export", export))

    app.run_polling()

if __name__ == "__main__":
    main()