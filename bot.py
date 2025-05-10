# bot.py – 支持四种模式：数字炸弹、数字扫雷、WenChi、酒鬼轮盘
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
group_data = {}

START_IMAGE = "https://i.imgur.com/NJg6mjJ.jpeg"
WENCHI_FAIL_IMAGE = "https://i.imgur.com/WeYjoPN.jpeg"

WHEEL_TASKS = [
    "你自己喝一杯！", "选一个人陪你喝！", "大家一起喝一杯！", "你安全了，选别人喝！",
    "真心话 or 喝1杯！", "本轮没事，不用喝！", "指定人喝，不限人数！", "本轮没事，下轮翻倍！"
]

def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💣 数字炸弹", callback_data="mode:bomb")],
        [InlineKeyboardButton("💥 数字扫雷", callback_data="mode:sweeper")],
        [InlineKeyboardButton("😋 WenChi 今天吃什么？", callback_data="mode:wenchi"),
         InlineKeyboardButton("🤤 酒鬼轮盘", callback_data="mode:wheel")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(photo=START_IMAGE, caption="欢迎来到多模式小游戏，请选择：", reply_markup=get_main_menu())

async def handle_mode_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    mode = query.data.split(":")[1]

    if mode == "wheel":
        group_data[chat_id] = {"players": [], "state": "waiting"}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="🍻 酒鬼轮盘开始啦！点击下方按钮参与！")
        await context.bot.send_message(
            chat_id=chat_id,
            text="点击「参加」按钮报名！",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍺 我要参加", callback_data="join:wheel")]
            ])
        )
    elif mode == "wenchi":
        await context.bot.send_message(chat_id=chat_id, text="WenChi 游戏尚未接入（保持原逻辑）")
    elif mode == "bomb":
        await context.bot.send_message(chat_id=chat_id, text="数字炸弹尚未接入（保持原逻辑）")
    elif mode == "sweeper":
        await context.bot.send_message(chat_id=chat_id, text="数字扫雷尚未接入（保持原逻辑）")

async def handle_wheel_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user = query.from_user

    if "players" not in group_data.get(chat_id, {}):
        group_data[chat_id] = {"players": [], "state": "waiting"}

    if user.id not in [p["id"] for p in group_data[chat_id]["players"]]:
        group_data[chat_id]["players"].append({"id": user.id, "name": user.full_name})

    player_names = "\n".join([f"- {p['name']}" for p in group_data[chat_id]["players"]])
    chosen = random.choice(group_data[chat_id]["players"])
    group_data[chat_id]["chosen"] = chosen["id"]

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ 当前参与者：\n{player_names}\n\n🎯 由 @{chosen['name']} 点击【旋转轮盘】！",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎡 旋转轮盘", callback_data="spin:wheel")]
        ])
    )

async def handle_wheel_spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user = query.from_user

    if group_data.get(chat_id, {}).get("chosen") != user.id:
        await query.answer("只有被点到的玩家可以旋转轮盘！", show_alert=True)
        return

    task = random.choice(WHEEL_TASKS)
    await context.bot.send_message(chat_id=chat_id, text=f"🍻 轮盘任务：{task}")
    group_data.pop(chat_id, None)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_mode_select, pattern="^mode:"))
    app.add_handler(CallbackQueryHandler(handle_wheel_join, pattern="^join:wheel$"))
    app.add_handler(CallbackQueryHandler(handle_wheel_spin, pattern="^spin:wheel$"))
    app.run_polling()

if __name__ == "__main__":
    main()