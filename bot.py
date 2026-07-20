import subprocess, os, threading

BOT_TOKEN = "8838617444:AAHUzG-DKVIalamCRc80-SjUT0cIR4_ZDKQ"  # BotFather se token lo

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
except:
    os.system('pip install python-telegram-bot')
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes

active = {}

async def start(update, context):
    await update.message.reply_text("🔥 BOT READY\n/bomb <number>\n/stop")

async def bomb(update, context):
    uid = update.effective_user.id
    if not context.args:
        await update.message.reply_text("/bomb 98XXXXXXXX")
        return
    target = context.args[0]
    if not target.isdigit() or len(target) != 10:
        await update.message.reply_text("Invalid number!")
        return
    if uid in active:
        await update.message.reply_text("Already bombing! Use /stop")
        return
    
    p = subprocess.Popen(['python', 'EGO.py', target])
    active[uid] = p
    await update.message.reply_text(f"💣 Bombing +91{target}\n🛑 /stop")

async def stop(update, context):
    uid = update.effective_user.id
    if uid in active:
        active[uid].kill()
        del active[uid]
        await update.message.reply_text("🛑 Stopped!")
    else:
        await update.message.reply_text("Nothing to stop!")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("bomb", bomb))
app.add_handler(CommandHandler("stop", stop))
print("Bot running...")
app.run_polling()
