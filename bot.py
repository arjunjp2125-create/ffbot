from dotenv import load_dotenv
load_dotenv("/data/data/com.termux/files/home/ffbot/.env")
import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 Free Fire Likes", callback_data="likes")],
        [InlineKeyboardButton("📦 My Orders", callback_data="orders")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]

    await update.message.reply_text(
        "🔥 Welcome to FreeFire Reseller!\n\n"
        "Select an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "likes":
        context.user_data["waiting_for_player_id"] = True
        await query.message.reply_text(
            "🎮 Free Fire Likes\n\n"
            "Please send your Player ID.\n\n"
            "⚠️ Never send your password or OTP."
        )

    elif query.data == "orders":
        await query.message.reply_text(
            "📦 Your orders\n\n"
            "Order history will be available here soon."
        )

    elif query.data == "help":
        await query.message.reply_text(
            "ℹ️ Help\n\n"
            "Send /start to open the main menu."
        )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_player_id"):
        await update.message.reply_text(
            "Please use /start to open the menu."
        )
        return

    player_id = update.message.text.strip()

    if not player_id.isdigit():
        await update.message.reply_text(
            "❌ Invalid Player ID.\n"
            "Please send numbers only."
        )
        return

    context.user_data["player_id"] = player_id
    context.user_data["waiting_for_player_id"] = False

    keyboard = [
        [InlineKeyboardButton("100 Likes", callback_data="qty_100")],
        [InlineKeyboardButton("500 Likes", callback_data="qty_500")],
        [InlineKeyboardButton("1000 Likes", callback_data="qty_1000")],
    ]

    await update.message.reply_text(
        f"✅ Player ID received: {player_id}\n\n"
        "Select quantity:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def quantity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quantity = query.data.replace("qty_", "")
    player_id = context.user_data.get("player_id")

    if not player_id:
        await query.message.reply_text(
            "❌ Player ID session expired. Please use /start again."
        )
        return

    await query.message.reply_text(
        "📝 Order Request\n\n"
        f"Player ID: {player_id}\n"
        f"Quantity: {quantity} likes\n\n"
        "⏳ Order system is being prepared.\n"
        "No payment has been taken."
    )


def main():
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=60.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    app = (
        Application.builder()
        .token(TOKEN)
        .request(request)
        .get_updates_request(request)
        .build()
    )

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(
            quantity_handler,
            pattern=r"^qty_"
        )
    )

    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
