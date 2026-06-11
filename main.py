import os
import json
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")

DB_FILE = "players.json"


def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🎲 Xúc xắc", callback_data="dice"),
        InlineKeyboardButton("🎯 Phi tiêu", callback_data="dart")
    ]]

    await update.message.reply_text(
        "🎮 Chọn trò chơi",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def play_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = str(user.id)

    today = datetime.now().strftime("%Y-%m-%d")

    data = load_data()

    if user_id in data and data[user_id]["date"] == today:
        await query.message.reply_text(
            "❌ Bạn đã chơi hôm nay rồi.\nHãy quay lại vào ngày mai."
        )
        return

    game = query.data

    total = 0
    results = []

    emoji = "🎲" if game == "dice" else "🎯"

    for _ in range(5):
        msg = await context.bot.send_dice(
            chat_id=query.message.chat_id,
            emoji=emoji
        )

        value = msg.dice.value
        total += value
        results.append(str(value))

    data[user_id] = {
        "username": user.username,
        "name": user.full_name,
        "score": total,
        "date": today,
        "game": game
    }

    save_data(data)

    await query.message.reply_text(
        f"{emoji} Kết quả\n\n"
        f"{' + '.join(results)}\n\n"
        f"🏆 Điểm của bạn: {total}/30"
    )


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(play_game))

print("Bot đang chạy...")
app.run_polling()
