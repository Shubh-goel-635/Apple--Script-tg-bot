BOT_TOKEN = "8476987280:AAFDZ_FSEheBxTf-2LyKmrBDOKyqsKfcVDA"
CHAT_ID = -1003686843772


async def send_message(bot, message):
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")


async def complete_message(bot):
    await bot.send_message(chat_id=CHAT_ID, text="🤖 Loop Completed")
