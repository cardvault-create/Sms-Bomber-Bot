#!/usr/bin/env python
import subprocess, os

BOT_TOKEN = "8838617444:AAHUzG-DKVIalamCRc80-SjUT0cIR4_ZDKQ"  # BotFather se token lo

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler
except ImportError:
    os.system('pip install python-telegram-bot --upgrade')
    from telegram import Update
    from telegram.ext import Application, CommandHandler

active_bombing = {}

async def start(update: Update, context):
    await update.message.reply_text("""
🔥 **BOMBER BOT**
@BeStChEaT_OwNeR

/bomb <10-digit-number>
/stop
""", parse_mode='Markdown')

async def bomb(update: Update, context):
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("❌ /bomb 98XXXXXXXX")
        return
    
    target = context.args[0]
    if not target.isdigit() or len(target) != 10:
        await update.message.reply_text("❌ Enter valid 10-digit number!")
        return
    
    if user_id in active_bombing:
        await update.message.reply_text("⚠️ Already bombing! Use /stop")
        return
    
    process = subprocess.Popen(
        ['python', 'EGO.py', target],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    active_bombing[user_id] = process
    
    await update.message.reply_text(f"💣 Bombing +91{target}\n🛑 /stop")

async def stop(update: Update, context):
    user_id = update.effective_user.id
    if user_id in active_bombing:
        active_bombing[user_id].kill()
        del active_bombing[user_id]
        await update.message.reply_text("🛑 Stopped!")
    else:
        await update.message.reply_text("No active bombing!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bomb", bomb))
    app.add_handler(CommandHandler("stop", stop))
    print("[+] Bot Running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
