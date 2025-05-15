import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from werewolf import (
    entry_game,
    set_mode,
    join_game,
    view_word,
    handle_vote,   
    handle_vote2,  
    start_game_restart
    )

# 全局游戏状态
group_mode = {}     # 每个群当前模式
group_data = {}     # 每个群当前游戏状态（炸弹数、扫雷状态、WenChi食物）

# 图片链接（请替换为你自己的）
MAIN_MENU_IMAGE = "https://i.imgur.com/4dwntl8.png"
START_IMAGE_Bomb = "https://i.imgur.com/gFvwBy3.png"
START_IMAGE_WenChi = "https://i.imgur.com/UjqvBCU.png"
START_IMAGE_JiuGui = "https://i.imgur.com/kms13rs.png"
BOMB_IMAGE = "https://i.imgur.com/uMwL0Du.png"
WENCHI_BOMB_IMAGE = "https://i.imgur.com/MtLkHEC.png"
VIDEO_JiuGui = "https://i.imgur.com/TQcVLSp.mp4"
ENG_JiuGui = "https://i.imgur.com/K1O0KnR.png"

food_options = [
    "酱到流油的烤鸡翅", "香到爆的猪肉串", "辣哭你的麻辣烫", "泡菜盖顶火锅面", "满满起司的炸年糕",
    "咬一口喷香烧肉饭", "一口爆汁的小笼包", "蘸满酱的泰式炸虾", "芝士狂魔披萨片", "三秒吞完的寿司卷"
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
        [InlineKeyboardButton("🤤 酒鬼轮盘", callback_data="mode:wheel")],
        [InlineKeyboardButton("5 - 谁是卧底", callback_data="game_werewolf")]
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
    await query.message.delete()
    mode = query.data.split(":")[1]
    chat_id = query.message.chat.id
    group_mode[chat_id] = mode
    if mode == "wenchi":
        bad = random.randint(1, 10)
        group_data[chat_id] = {"bad": bad, "selected": set()}

        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE_WenChi, caption="😋 WenChi 今天吃什么？请选择：", reply_markup=get_food_keyboard())

    elif mode == "sweeper":
        group_data[chat_id] = {"min": 1, "max": 100, "bomb": random.randint(1, 100)}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE_Bomb, caption="💥 数字扫雷开始！范围：1–100，直接发送数字猜测！")
    elif mode == "bomb":
        keyboard = [[InlineKeyboardButton(f"{i} 💣", callback_data=f"bombs:{i}") for i in range(1, 4)]]
        await context.bot.send_message(chat_id=chat_id, text="请选择本局💣的数量‼越多越刺激‼", reply_markup=InlineKeyboardMarkup(keyboard))

    elif mode == "wheel":
        msg = await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE_JiuGui, caption="🍻酒鬼轮盘开始了！🕒倒计时60秒\n\n点击「🍺 我要参加」一起玩！",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍺 我要参加", callback_data="join:wheel")]
            ])
        )
        group_data.setdefault(chat_id, {"players": [], "state": "waiting"})
        group_data[chat_id]["join_msg_id"] = msg.message_id



        # 🕒 启动 60 秒倒计时任务
        context.application.job_queue.run_once(
            start_wheel_game,
            when=60,
            data={'chat_id': chat_id}
        )

async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_reply_markup(reply_markup=None)

    chat_id = query.message.chat.id
    mode = group_mode.get(chat_id)

    if mode == "bomb":
        keyboard = [[InlineKeyboardButton(f"{i} 💣", callback_data=f"bombs:{i}") for i in range(1, 4)]]
        await context.bot.send_message(chat_id=chat_id, text="请选择本局💣的数量‼越多越刺激‼", reply_markup=InlineKeyboardMarkup(keyboard))

    elif mode == "sweeper":
        group_data[chat_id] = {"min": 1, "max": 100, "bomb": random.randint(1, 100)}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE_Bomb, caption="💥 数字扫雷开始！范围：1–100，直接发送数字猜测！")

    elif mode == "wenchi":
        bad = random.randint(1, 10)
        group_data[chat_id] = {"bad": bad, "selected": set()}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE_WenChi, caption="😋 WenChi 今天吃什么？请选择：", reply_markup=get_food_keyboard())

    elif mode == "wheel":
        group_data[chat_id] = {"players": [], "state": "waiting"}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE_JiuGui, caption="🍻酒鬼轮盘开始了！🕒倒计时60秒\n\n点击「🍺 我要参加」一起玩！",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍺 我要参加", callback_data="join:wheel")]
            ])
        )
        context.application.job_queue.run_once(
            start_wheel_game,
            when=60,
            data={'chat_id': chat_id}
        )


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.edit_reply_markup(reply_markup=None)
    await send_main_menu(update.effective_chat.id, context)

async def handle_bomb_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    count = int(query.data.split(":")[1])
    chat_id = query.message.chat.id
    bombs = random.sample(range(1, 11), k=count)
    group_data[chat_id] = {"bombs": bombs, "selected": set()}
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMAGE_Bomb,
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
    "点名！选个人帮你喝！",
    "干杯！全员一起喝！",
    "倒满，自己干了！",
    "拉个倒霉蛋来喝",
    "剪刀石头布，输的喝！",
    "喊 5/10/15，谁输谁喝！",
    "指定人喝，不限人数！",
    "恭喜你，不用喝！"
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
    join_msg_id = data.get("join_msg_id")
    if join_msg_id:
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=join_msg_id,
                reply_markup=None
            )
        except:
            pass
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
    await context.bot.send_video(
        chat_id,video=VIDEO_JiuGui,
        supports_streaming=True,
        caption=f"🎯 @{current['name']} 请点击下方按钮旋转轮盘！",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎡 旋转轮盘", callback_data="spin:wheel")]])
    )

async def handle_wheel_spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
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

    await query.message.edit_reply_markup(reply_markup=None)

    task = random.choice(WHEEL_TASKS)
    await context.bot.send_message(chat_id=chat_id, text=f"🍻 @{user.full_name} 抽到任务：{task}")

    await asyncio.sleep(5)

    data["current"] += 1
    if data["current"] >= len(players):
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=ENG_JiuGui,
            caption="🎊 本轮游戏结束，你醉了吗？",
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
    app.add_handler(CallbackQueryHandler(entry_game, pattern="^game_werewolf$"))
    app.add_handler(CallbackQueryHandler(set_mode, pattern="^werewolf:mode:"))
    app.add_handler(CallbackQueryHandler(join_game, pattern="^werewolf_join$"))
    app.add_handler(CallbackQueryHandler(view_word, pattern="^werewolf_view$"))
    app.add_handler(CallbackQueryHandler(handle_vote, pattern="^werewolf:vote:"))
    app.add_handler(CallbackQueryHandler(handle_vote2, pattern="^werewolf:vote2:"))
    app.add_handler(CallbackQueryHandler(start_game_restart, pattern="^werewolf:restart$"))
    

    print("✅ 多模式游戏 Bot 正在运行")
    app.run_polling()
