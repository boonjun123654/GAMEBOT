import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# 全局游戏状态
group_mode = {}     # 每个群当前模式
group_data = {}     # 每个群当前游戏状态（炸弹数、扫雷状态、WenChi食物）

# 图片链接（请替换为你自己的）
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
    keyboard = []
    row = []
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
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=MAIN_MENU_IMAGE,
        caption="欢迎加入游戏！请选择你要玩的模式：",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="😋 WenChi 今天吃什么？请选择：",
        reply_markup=get_food_keyboard())

    elif mode == "sweeper":
        group_data[chat_id] = {"min": 1, "max": 100, "bomb": random.randint(1, 100)}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="💥 数字扫雷开始！范围：1–100，直接发送数字猜测！")
    elif mode == "bomb":
        keyboard = [[InlineKeyboardButton(f"{i} 💣", callback_data=f"bombs:{i}") for i in range(1, 4)]]
        await context.bot.send_message(chat_id=chat_id, text="请选择本局💣的数量‼越多越刺激‼", reply_markup=InlineKeyboardMarkup(keyboard))

    elif mode == "wheel":
        group_data[chat_id] = {"players": [], "state": "waiting"}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="🍻酒鬼轮盘开始了！🕒倒计时60秒\n\n点击「🍺 我要参加」一起玩！",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍺 我要参加", callback_data="join:wheel")]
            ])
        )

        # 🕒 启动 60 秒倒计时任务
        context.application.job_queue.run_once(
            start_wheel_game,
            when=60,
            data={'chat_id': chat_id}
        )


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

    if chat_id not in group_data or not isinstance(group_data[chat_id], dict):
        group_data[chat_id] = {"bad": bad, "selected": set()}
    else:
        group_data[chat_id]["bad"] = bad
        group_data[chat_id]["selected"] = set()
    await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE, caption="😋 WenChi 今天吃什么？游戏开始！")
    await context.bot.send_message(chat_id=chat_id, text="😋 WenChi 今天吃什么？请选择：", reply_markup=get_food_keyboard())

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_main_menu(update.effective_chat.id, context)

async def handle_bomb_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    count = int(query.data.split(":")[1])
    chat_id = query.message.chat.id
    bombs = random.sample(range(1, 11), k=count)
    group_data[chat_id] = {"bombs": bombs, "selected": set()}
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMAGE,
        caption="游戏开始！💣炸弹数字已准备！\n请根据顺序点选号码！",
        reply_markup=get_bomb_keyboard()
    )

async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    number = int(query.data.split(":")[1])
    data = group_data.get(chat_id)
    if not data or "bombs" not in data:
        return
    
    if number in data["selected"]:
        await query.answer("这个数字已经被选过了！", show_alert=True)
        return

    
    data["selected"].add(number)
    if number in data["bombs"]:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=BOMB_IMAGE,
            caption=f"💣Boom！{query.from_user.first_name} 踩中炸弹！",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 重新开始", callback_data="restart")],
                [InlineKeyboardButton("🎮 切换游戏模式", callback_data="mainmenu")]
            ])
        )
        group_data.pop(chat_id, None)
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"{query.from_user.first_name} 选择了数字：{number}")

async def handle_wenchi_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    guess = int(query.data.split(":")[1])
    bad = group_data.get(chat_id, {}).get("bad")
    
    if chat_id not in group_data:
        group_data[chat_id] = {"selected": set()}
    if "selected" not in group_data[chat_id]:
        group_data[chat_id]["selected"] = set()
    if guess in group_data[chat_id]["selected"]:
        await query.answer("这个食物已经被选过了~", show_alert=True)
        return
    group_data[chat_id]["selected"].add(guess)

    if isinstance(bad, int) and guess == bad:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=WENCHI_BOMB_IMAGE,
            caption=f"Oh no！WenChi吃坏肚子了！他选择的是「{food_options[guess-1]}」",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 重新开始", callback_data="restart")],
                [InlineKeyboardButton("🎮 切换游戏模式", callback_data="mainmenu")]
            ])
        )
        group_data.pop(chat_id, None)
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"{food_options[guess - 1]} 很安全😋")

async def handle_sweeper_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if group_mode.get(chat_id) != "sweeper":
        return
    text = update.message.text.strip()
    if not text.isdigit():
        return
    guess = int(text)
    data = group_data.get(chat_id)
    if not data:
        return
    if guess == data["bomb"]:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=BOMB_IMAGE,
            caption=f"💥 Boom！{update.effective_user.first_name} 猜中了炸弹！",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 重新开始", callback_data="restart")],
                [InlineKeyboardButton("🎮 切换游戏模式", callback_data="mainmenu")]
            ])
        )
        group_data.pop(chat_id, None)
    elif guess < data["bomb"]:
        data["min"] = max(data["min"], guess + 1)
        await context.bot.send_message(chat_id=chat_id, text=f"太小了！当前范围：{data['min']} - {data['max']}")
    else:
        data["max"] = min(data["max"], guess - 1)
        await context.bot.send_message(chat_id=chat_id, text=f"太大了！当前范围：{data['min']} - {data['max']}")

# ====== 🍻 酒鬼轮盘模块 ======

import asyncio

WHEEL_TASKS = [
    "你自己喝一杯！",
    "选一个人陪你喝！",
    "大家一起喝一杯！",
    "你安全了，选别人喝！",
    "真心话 or 喝1杯！",
    "本轮没事，不用喝！",
    "指定人喝，不限人数！",
    "找一个人玩剪刀石头布，输了喝一杯！"
]

async def handle_wheel_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user = query.from_user

    if "players" not in group_data.get(chat_id, {}):
        group_data[chat_id] = {"players": [], "state": "waiting", "current": 0}

    players = group_data[chat_id]["players"]

    if user.id not in [p["id"] for p in players]:
        players.append({"id": user.id, "name": user.full_name})
        await context.bot.send_message(chat_id=chat_id, text=f"{user.full_name} 已报名 📝")

    if group_data[chat_id]["state"] == "waiting":
        group_data[chat_id]["state"] = "counting"

    else:
        await query.answer("你已经报名了！", show_alert=True)


async def start_wheel_game(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data['chat_id']
    data = group_data.get(chat_id)
    if not data or not data.get("players"):
        await context.bot.send_message(chat_id, "❌ 没有玩家参与，游戏取消。")
        group_data.pop(chat_id, None)
        return

    players = data["players"]
    names = "\n".join(f"{i+1}. {p['name']}" for i, p in enumerate(players))
    data["state"] = "playing"
    data["current"] = 0

    await context.bot.send_message(chat_id, f"🎉 报名结束！本轮玩家：\n{names}")

    current = players[0]
    await context.bot.send_message(
        chat_id,
        text=f"🎯 @{current['name']} 请点击下方按钮旋转轮盘！",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎡 旋转轮盘", callback_data="spin:wheel")]])
    )

async def handle_wheel_spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user = query.from_user
    data = group_data.get(chat_id)

    if not data or data["state"] != "playing":
        return

    players = data["players"]
    current_index = data["current"]

    if players[current_index]["id"] != user.id:
        await query.answer("请等待轮到你再点击！", show_alert=True)
        return

    task = random.choice(WHEEL_TASKS)
    await context.bot.send_message(chat_id=chat_id, text=f"🍻 @{user.full_name} 抽到任务：{task}")

    data["current"] += 1
    if data["current"] >= len(players):
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=START_IMAGE,
            caption="🎊 本轮酒鬼轮盘结束啦！感谢参与！",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 重新开始", callback_data="restart")],
                [InlineKeyboardButton("🎮 切换游戏模式", callback_data="mainmenu")]
            ])
        )
        group_data.pop(chat_id, None)
    else:
        next_player = players[data["current"]]
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎯 轮到 @{next_player['name']}，请点击旋转轮盘！",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎡 旋转轮盘", callback_data="spin:wheel")]
            ])
        )

if __name__ == "__main__":

    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    job_queue = app.job_queue  # ⬅️ 确保 job_queue 激活

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(开始游戏)$"), start_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.TEXT, handle_sweeper_input))
    app.add_handler(CallbackQueryHandler(handle_mode_select, pattern="^mode:"))
    app.add_handler(CallbackQueryHandler(handle_bomb_count, pattern="^bombs:"))
    app.add_handler(CallbackQueryHandler(handle_guess, pattern="^guess:"))
    app.add_handler(CallbackQueryHandler(handle_wenchi_guess, pattern="^wenchi:"))
    app.add_handler(CallbackQueryHandler(handle_restart, pattern="^restart$"))
    app.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^mainmenu$"))
    app.add_handler(CallbackQueryHandler(handle_wheel_join, pattern="^join:wheel$"))
    app.add_handler(CallbackQueryHandler(handle_wheel_spin, pattern="^spin:wheel$"))


    print("✅ 多模式游戏 Bot 正在运行")
    app.run_polling()
