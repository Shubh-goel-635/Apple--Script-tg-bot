import asyncio
import json
import os
import queue

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from dotenv import load_dotenv
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from StopSignal import stop_event

from StockCheck import product_stock_loop

queue = asyncio.Queue()  # shared queue
stock_task = None
sender_task = None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('start')
    global stock_task, sender_task, queue, stop_event
    stop_event.clear()  # reset stop signal

    # Start Telegram sender if not running
    if sender_task is None or sender_task.done():
        sender_task = asyncio.create_task(telegram_sender(context.bot, queue))

    # Start stock checking
    if stock_task is None or stock_task.done():
        stock_task = asyncio.create_task(product_stock_loop(queue))
        await update.message.reply_text("✅ Stock checking started!")
    else:
        await update.message.reply_text("⚠️ Stock checking is already running.")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('stop')
    global stock_task, sender_task, stop_event
    stop_event.set()  # signal loops to stop

    if stock_task is not None:
        stock_task.cancel()
        stock_task = None

    # Stop sender task
    if sender_task is not None:
        await queue.put(None)  # to unblock the sender
        await sender_task
        sender_task = None

    await update.message.reply_text("🛑 Stock checking stopped!")


# Telegram sender
async def telegram_sender(bot, queue):
    while True:
        message = await queue.get()
        if message is None:  # stop signal
            break
        try:
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        except Exception as e:
            print("Telegram send error:", e)
        finally:
            queue.task_done()


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return  # silence logs (optional)


def run_health_server():
    server = HTTPServer(("0.0.0.0", 10000), HealthHandler)
    server.serve_forever()


threading.Thread(target=run_health_server, daemon=True).start()

load_dotenv(dotenv_path='local.env', override=False)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
print(BOT_TOKEN)
print(CHAT_ID)
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("stop", stop_command))

print("Bot is running...")
if __name__ == "__main__":
    app.run_polling()
