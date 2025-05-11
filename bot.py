import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CallbackQueryHandler,
    MessageHandler, filters, CallbackContext
)

# 游戏状态数据
group_mode = {}
group_data = {}

# 图片链接
MAIN_MENU_IMAGE = "https://i.imgur.com/xu8tzYq.png"
START_IMAGE = "https://i.imgur.com/XtN6aR5.png"
BOMB_IMAGE = "https://i.imgur.com/lEZtM13.jpeg"
WENCHI_BOMB_IMAGE = "https://i.imgur.com/7KaGX4P.png"

food_options = [
    "泰国餐", "泰式烧烤", "韩式烧烤", "啦啦煲", "越南餐",
    "中国餐", "火锅", "BBQ", "酸菜鱼", "日式火锅"
]

def get_food_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f, callback_data=f"wenchi:{i+1}")]
        for i, f in enumerate(food_options)
    ])

def get_bomb_keyboard():
    keyboard, row = [], []
    for i in range(1, 11):
        row.append(InlineKeyboardButton(str(i), callback_data=f"guess:{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    return InlineKeyboardMarkup(keyboard)

async def send_main_menu(chat_id, context):
    keyboard = [
        [InlineKeyboardButton("💣 数字炸弹", callback_data="mode:bomb")],
        [InlineKeyboardButton("💥 数字扫雷", callback_data="mode:sweeper")],
        [InlineKeyboardButton("😋 WenChi 今天吃什么？", callback_data="mode:wenchi")],
        [InlineKeyboardButton("🤤 酒鬼轮盘", callback_data="mode:wheel")]
    ]
    await context.bot.send_photo(chat_id=chat_id, photo=MAIN_MENU_IMAGE,
        caption="欢迎加入游戏！请选择你要玩的模式：", reply_markup=InlineKeyboardMarkup(keyboard))

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_main_menu(update.effective_chat.id, context)

async def handle_mode_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data.split(":")[1]
    chat_id = query.message.chat.id
    group_mode[chat_id] = mode
    if mode == "wenchi":
        bad_food = random.randint(1, 10)
        group_data[chat_id] = {"bad": bad_food, "selected": set()}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="😋 WenChi 今天吃什么？游戏开始！")
        await context.bot.send_message(chat_id=chat_id, text="😋 WenChi 今天吃什么？请选择：", reply_markup=get_food_keyboard())
    elif mode == "sweeper":
        group_data[chat_id] = {"min": 1, "max": 100, "bomb": random.randint(1, 100)}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="💥 数字扫雷游戏开始！范围：1–100")
        await context.bot.send_message(chat_id=chat_id, text="💥 数字扫雷开始！范围：1–100，直接发送数字猜测！")
    elif mode == "bomb":
        keyboard = [[InlineKeyboardButton(f"{i} 💣", callback_data=f"bombs:{i}") for i in range(1, 4)]]
        await context.bot.send_message(chat_id=chat_id, text="请选择本局💣的数量‼越多越刺激‼", reply_markup=InlineKeyboardMarkup(keyboard))
    elif mode == "wheel":
        group_data[chat_id] = {"players": [], "state": "waiting"}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="🍻 酒鬼轮盘开始啦！点击下方按钮参与！")
        await context.bot.send_message(chat_id=chat_id, text="点击「参加」按钮报名！", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🍺 我要参加", callback_data="join:wheel")]
        ]))
        context.job_queue.run_once(start_wheel_job, 60, data=chat_id)
        await context.bot.send_message(chat_id=chat_id, text="⏳ 60 秒后开始轮盘！等待其他人加入...")

async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    mode = group_mode.get(chat_id)
    if mode == "bomb":
        keyboard = [[InlineKeyboardButton(f"{i} 💣", callback_data=f"bombs:{i}") for i in range(1, 4)]]
        await context.bot.send_message(chat_id=chat_id, text="请选择本局💣的数量‼越多越刺激‼", reply_markup=InlineKeyboardMarkup(keyboard))
    elif mode == "sweeper":
        group_data[chat_id] = {"min": 1, "max": 100, "bomb": random.randint(1, 100)}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="💥 数字扫雷游戏开始！范围：1–100")
        await context.bot.send_message(chat_id=chat_id, text="💥 数字扫雷开始！范围：1–100，直接发送数字猜测！")
    elif mode == "wenchi":
        bad = random.randint(1, 10)
        group_data[chat_id] = {"bad": bad, "selected": set()}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="😋 WenChi 今天吃什么？游戏开始！")
        await context.bot.send_message(chat_id=chat_id, text="😋 WenChi 今天吃什么？请选择：", reply_markup=get_food_keyboard())

# wheel join handler（倒计时在 mode:wheel 中已经启动）
async def handle_wheel_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user = query.from_user
    data = group_data.get(chat_id)
    if not data:
        group_data[chat_id] = {"players": [], "state": "waiting"}
        data = group_data[chat_id]
    if user.id not in [p["id"] for p in data["players"]]:
        data["players"].append({"id": user.id, "name": user.full_name})
        await context.bot.send_message(chat_id=chat_id, text=f"{user.full_name} 已报名 ✅")
    else:
        await query.answer("你已经报名了！", show_alert=True)

def start_wheel_job(context: CallbackContext):
    asyncio.create_task(start_wheel_game(context))

async def start_wheel_game(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    data = group_data.get(chat_id)
    if not data or not data.get("players"):
        await context.bot.send_message(chat_id=chat_id, text="❌ 没有玩家参与，游戏取消。")
        group_data.pop(chat_id, None)
        return
    players = data["players"]
    names = "\n".join([f"{i+1}. {p['name']}" for i, p in enumerate(players)])
    data["state"] = "playing"
    data["current"] = 0
    await context.bot.send_message(chat_id=chat_id, text=f"✅ 报名结束！本轮玩家：\n{names}")
    current_player = players[0]
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🎯 @{current_player['name']} 请点击下方按钮旋转轮盘！",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎡 旋转轮盘", callback_data="spin:wheel")]
        ])
    )

# 启动
if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(开始游戏)$"), start_command))
    app.add_handler(CallbackQueryHandler(handle_mode_select, pattern="^mode:"))
    app.add_handler(CallbackQueryHandler(handle_restart, pattern="^restart$"))
    app.add_handler(CallbackQueryHandler(handle_wheel_join, pattern="^join:wheel$"))
    print("✅ Bot 已启动")
    job_queue = app.job_queue
    app.run_polling()