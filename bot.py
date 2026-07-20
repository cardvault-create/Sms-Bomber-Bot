#!/usr/bin/env python
import subprocess, os, sys, asyncio

BOT_TOKEN = "8838617444:AAHUzG-DKVIalamCRc80-SjUT0cIR4_ZDKQ"  # BotFather se mila token yahan dalo

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    from telegram.error import TelegramError
except ImportError:
    os.system('pip install python-telegram-bot --upgrade')
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    from telegram.error import TelegramError

active_bombing = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🔥 BOMBER BOT 🔥
Created By: @BeStChEaT_OwNeR

/bomb <number> - Start
/stop - Stop
""")

async def bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Usage: /bomb 9876543210")
        return
    
    target = context.args[0]
    if not target.isdigit() or len(target) != 10:
        await update.message.reply_text("Invalid number!")
        return
    
    if user_id in active_bombing:
        await update.message.reply_text("Already bombing!")
        return
    
    process = subprocess.Popen(
        ['python', 'bomber.py', target],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    active_bombing[user_id] = (process, target)
    await update.message.reply_text(f"💣 Bombing +91{target}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_bombing:
        process, target = active_bombing.pop(user_id)
        process.kill()
        await update.message.reply_text("🛑 Stopped!")
    else:
        await update.message.reply_text("No bombing active!")

async def error_handler(update, context):
    print(f"Error: {context.error}")
    try:
        raise context.error
    except TelegramError:
        pass

def main():
    print("[+] Starting Bot...")
    
    # Timeout badhao Railway ke liye
    app = Application.builder().token(BOT_TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bomb", bomb))
    app.add_handler(CommandHandler("stop", stop))
    app.add_error_handler(error_handler)
    
    print("[+] Bot Running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
