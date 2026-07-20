#!/usr/bin/env python
import subprocess
import threading
import os
import sys

BOT_TOKEN = "8838617444:AAHUzG-DKVIalamCRc80-SjUT0cIR4_ZDKQ"

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
except ImportError:
    os.system('pip install python-telegram-bot --upgrade')
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes

active_bombing = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """
🔥 **BOMBER BOT** 🔥

Created By: **@BeStChEaT_OwNeR**
For Educational Purpose Only

Commands:
/bomb <10_digit_number>
/stop

Example:
/bomb 9876543210
"""
    await update.message.reply_text(msg, parse_mode='Markdown')

async def bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /bomb 9876543210")
        return
    
    target = context.args[0]
    
    if not target.isdigit() or len(target) != 10:
        await update.message.reply_text("❌ Enter valid 10-digit number!")
        return
    
    if user_id in active_bombing:
        await update.message.reply_text("⚠️ Already bombing! Use /stop first.")
        return
    
    process = subprocess.Popen(
        ['python', 'bomber.py', target],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    active_bombing[user_id] = (process, target)
    
    await update.message.reply_text(f"""
💣 **BOMBING STARTED**
📱 Target: +91{target}
🔴 Use /stop to stop

**@BeStChEaT_OwNeR**
""", parse_mode='Markdown')

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in active_bombing:
        await update.message.reply_text("❌ No active bombing!")
        return
    
    process, target = active_bombing.pop(user_id)
    process.kill()
    
    await update.message.reply_text(f"""
🛑 **BOMBING STOPPED**
📱 Target: +91{target}

**@BeStChEaT_OwNeR**
""", parse_mode='Markdown')

def main():
    print("[+] Bot Starting...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bomb", bomb))
    app.add_handler(CommandHandler("stop", stop))
    print("[+] Bot Running!")
    app.run_polling()

if __name__ == '__main__':
    main()
