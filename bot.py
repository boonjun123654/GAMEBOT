import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, JobQueue
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
group_data = {}

START_IMAGE = "https://i.imgur.com/NJg6mjJ.jpeg"
WHEEL_TASKS = [
    "你自己喝一杯！", "选一个人陪你喝！", "大家一起喝一杯！", "你安全了，选别人喝！",
    "真心话 or 喝1杯！", "本轮没事，不用喝！", "指定人喝，不限人数！", "本轮没事，下轮翻倍！"
]

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💣 数字炸弹", callback_data="mode:bomb")],
        [InlineKeyboardButton("💥 数字扫雷", callback_data="mode:sweeper")],
        [InlineKeyboardButton("😋 WenChi 今天吃什么？", callback_data="mode:wenchi")],
        [InlineKeyboardButton("🍻 酒鬼轮盘", callback_data="mode:wheel")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(photo=START_IMAGE, caption="欢迎来到多模式小游戏，请选择：", reply_markup=get_main_menu())

async def handle_mode_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    mode = query.data.split(":")[1]

    if mode == "wheel":
        group_data[chat_id] = {"players": [], "state": "waiting", "current": 0}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="🍻 酒鬼轮盘开始啦！点击【我要参加】报名！")
        await context.bot.send_message(
            chat_id=chat_id,
            text="🕒 倒计时 60 秒后开始游戏，大家快报名！",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍻 我要参加", callback_data="join:wheel")]
            ])
        )
        await context.job_queue.run_once(start_wheel_game, 60, data=chat_id)

    elif mode == "wenchi":
        await context.bot.send_message(chat_id=chat_id, text="（保留 WenChi 游戏逻辑）")

    elif mode == "bomb":
        await context.bot.send_message(chat_id=chat_id, text="（保留数字炸弹逻辑）")

    elif mode == "sweeper":
        await context.bot.send_message(chat_id=chat_id, text="（保留数字扫雷逻辑）")

async def handle_wheel_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user = query.from_user

    data = group_data.get(chat_id)
    if not data or "players" not in data:
        return

    if user.id not in [p["id"] for p in data["players"]]:
        data["players"].append({"id": user.id, "name": user.full_name})
        await context.bot.send_message(chat_id=chat_id, text=f"{user.full_name} 已报名 ✅")

async def start_wheel_game(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    data = group_data.get(chat_id)
    if not data or not data.get("players"):
        await context.bot.send_message(chat_id=chat_id, text="😥 没有人报名，轮盘游戏取消。")
        group_data.pop(chat_id, None)
        return

    players = data["players"]
    names = "\n".join([f"- {p['name']}" for p in players])
    current_player = players[0]

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ 报名结束，{len(players)} 位玩家参加。
🎯 当前轮到：@{current_player['name']}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎡 旋转轮盘", callback_data="spin:wheel")]
        ])
    )
    data["state"] = "playing"

async def handle_wheel_spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user = query.from_user
    data = group_data.get(chat_id)

    if not data or data["state"] != "playing":
        return

    current_index = data["current"]
    players = data["players"]
    if players[current_index]["id"] != user.id:
        await query.answer("还没轮到你哦～", show_alert=True)
        return

    task = random.choice(WHEEL_TASKS)
    await context.bot.send_message(chat_id=chat_id, text=f"🎡 {user.full_name} 转到：{task}")

    # 下一个玩家
    data["current"] += 1
    if data["current"] >= len(players):
        await context.bot.send_message(chat_id=chat_id, text="✅ 所有人都完成任务啦！🎉 游戏结束～")
        group_data.pop(chat_id, None)
        return

    next_player = players[data["current"]]
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🎯 到 @{next_player['name']} 啦！",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎡 旋转轮盘", callback_data="spin:wheel")]
        ])
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_mode_select, pattern="^mode:"))
    app.add_handler(CallbackQueryHandler(handle_wheel_join, pattern="^join:wheel$"))
    app.add_handler(CallbackQueryHandler(handle_wheel_spin, pattern="^spin:wheel$"))
    app.run_polling()

if __name__ == "__main__":
    main()