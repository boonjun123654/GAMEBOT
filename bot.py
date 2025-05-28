import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from werewolf import (
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
MAIN_MENU_IMAGE = "https://i.imgur.com/ImNHwGk.jpeg"
START_IMAGE_Bomb = "https://i.imgur.com/wcRbnSG.jpeg"
START_IMAGE_Bomb2 = "https://i.imgur.com/HdFmGiv.jpeg"
BOMB_IMAGE = "https://i.imgur.com/UZ1RDaQ.jpeg"


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
        [InlineKeyboardButton("🕵️‍♂️ 谁是卧底", callback_data="game_werewolf")]
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
    if mode == "sweeper":
        group_data[chat_id] = {"min": 1, "max": 100, "bomb": random.randint(1, 100)}
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE_Bomb2, caption="💥 数字扫雷开始！范围：1–100，直接发送数字猜测！")
    elif mode == "bomb":
        keyboard = [[InlineKeyboardButton(f"{i} 💣", callback_data=f"bombs:{i}") for i in range(1, 4)]]
        await context.bot.send_message(chat_id=chat_id, text="请选择本局💣的数量‼越多越刺激‼", reply_markup=InlineKeyboardMarkup(keyboard))


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
        await context.bot.send_photo(chat_id=chat_id, photo=START_IMAGE_Bomb2, caption="💥 数字扫雷开始！范围：1–100，直接发送数字猜测！")


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
    user = query.from_user
    number = int(query.data.split(":")[1])
    data = group_data.get(chat_id)
    if not data or "bombs" not in data:
        return
    
    if number in data["selected"]:
        await query.answer("这个数字已经被选过了！", show_alert=True)
        return

    
    bombs = data["bombs"]  # ⬅️ 添加
    if number in data["selected"]:
        await query.answer("这个数字已经被选过了！", show_alert=True)
        return

    data["selected"].add(number)

    if number in bombs:  # ⬅️ 用 number 判断
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=BOMB_IMAGE,
            caption=f"💣 Boom！{user.first_name} 猜中炸弹，请接受惩罚！",
            reply_markup=get_punishment_buttons()
        )
        group_data.pop(chat_id, None)
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"{user.first_name} 选择了数字：{number}")

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
    user = update.effective_user
    if guess == data["bomb"]:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=BOMB_IMAGE,
            caption=f"💣 Boom! {user.first_name} 猜中炸弹（{data['bomb']}），请接受惩罚！",
            reply_markup=get_punishment_buttons()
        )
        group_data.pop(chat_id, None)

    elif guess < data["bomb"]:
        data["min"] = max(data["min"], guess + 1)
        await context.bot.send_message(chat_id=chat_id, text=f"太小了！当前范围：{data['min']} - {data['max']}")
    else:
        data["max"] = min(data["max"], guess - 1)
        await context.bot.send_message(chat_id=chat_id, text=f"太大了！当前范围：{data['min']} - {data['max']}")

def get_punishment_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 进入惩罚轮盘", url="https://boonjun123654.github.io/punishment-task")],
        [
            InlineKeyboardButton("🔁 重新开始", callback_data="restart"),
            InlineKeyboardButton("🎮 切换游戏模式", callback_data="main")
        ]
    ])



if __name__ == "__main__":

    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    job_queue = app.job_queue  # ⬅️ 确保 job_queue 激活

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(开始游戏)$"), start_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.TEXT, handle_sweeper_input))
    app.add_handler(CallbackQueryHandler(handle_mode_select, pattern="^mode:"))
    app.add_handler(CallbackQueryHandler(handle_bomb_count, pattern="^bombs:"))
    app.add_handler(CallbackQueryHandler(handle_guess, pattern="^guess:"))
    app.add_handler(CallbackQueryHandler(handle_restart, pattern="^restart$"))
    app.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^mainmenu$"))
    app.add_handler(CallbackQueryHandler(set_mode, pattern="^game_werewolf$"))
    app.add_handler(CallbackQueryHandler(join_game, pattern="^werewolf:join$"))
    app.add_handler(CallbackQueryHandler(view_word, pattern="^werewolf:view$"))
    app.add_handler(CallbackQueryHandler(handle_vote, pattern="^werewolf:vote:"))
    app.add_handler(CallbackQueryHandler(handle_vote2, pattern="^werewolf:vote2:"))
    app.add_handler(CallbackQueryHandler(start_game_restart, pattern="^werewolf:restart$"))
    

    print("✅ 多模式游戏 Bot 正在运行")
    app.run_polling()
