# werewolf_bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
import asyncio
import random

game_state = {
    "mode": None,
    "players": [],
    "player_words": {},
    "undercover": None,
    "whiteboard": None,
    "word_pair": ("", ""),
    "status": "idle",
    "chat_id": None
}

word_pairs = [
    ("沙发", "床"), ("苹果", "梨"), ("飞机", "火箭"),
    ("医生", "护士"), ("篮球", "排球"), ("电视", "显示器"),
    ("猫", "老虎"), ("火锅", "烧烤"), ("牛奶", "豆浆")
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("谁是卧底", callback_data="game_werewolf")]]
    await update.message.reply_text("欢迎进入游戏菜单：", reply_markup=InlineKeyboardMarkup(keyboard))

async def entry_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("群组中进行", callback_data="mode_group")],
        [InlineKeyboardButton("现实世界进行", callback_data="mode_real")]
    ]
    await query.edit_message_text("请选择游戏模式：", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data.replace("mode_", "")
    game_state.update({
        "mode": mode,
        "players": [],
        "player_words": {},
        "undercover": None,
        "whiteboard": None,
        "word_pair": ("", ""),
        "status": "registering",
        "chat_id": query.message.chat_id
    })
    keyboard = [[InlineKeyboardButton("我要参加", callback_data="join_game")]]
    await query.edit_message_text(
        f"模式设定为：{mode}\n请在60秒内点击下方按钮报名：",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.job_queue.run_once(end_registration, 60, data=query.message.chat_id)

async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    uname = query.from_user.full_name
    await query.answer("你已报名！", show_alert=True)
    if uid not in game_state["players"]:
        game_state["players"].append(uid)
        context.bot_data[uid] = {"name": uname}
    keyboard = [[InlineKeyboardButton("我要参加", callback_data="join_game")]]
    await query.edit_message_text(
        f"当前已报名人数：{len(game_state['players'])}\n点击继续加入（剩余时间内）",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def end_registration(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    bot = context.bot
    players = game_state["players"]

    if len(players) < 4:
        await bot.send_message(chat_id, "人数不足，游戏取消。")
        game_state["status"] = "idle"
        return

    pair = random.choice(word_pairs)
    game_state["word_pair"] = pair
    random.shuffle(players)
    game_state["undercover"] = players[-1]
    if len(players) >= 7:
        game_state["whiteboard"] = players[-2]

    for uid in players:
        if uid == game_state["undercover"]:
            game_state["player_words"][uid] = pair[1]
        elif uid == game_state["whiteboard"]:
            game_state["player_words"][uid] = ""
        else:
            game_state["player_words"][uid] = pair[0]

    for uid in players:
        word = game_state["player_words"][uid]
        await bot.send_message(uid, f"你获得的词语是：{'（空白）' if word == '' else word}")
        btn = [[InlineKeyboardButton("查看我的词语", callback_data="view_word")]]
        await bot.send_message(uid, "如需再次查看，请点击：", reply_markup=InlineKeyboardMarkup(btn))

    await bot.send_message(chat_id, "游戏开始！词语已发出，请准备描述。")
    await start_description_phase(chat_id, context)

async def start_description_phase(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    players = game_state["players"]
    await bot.send_message(
        chat_id,
        "描述阶段开始！请每位玩家用一句话描述你的词语。\n⚠️ 请真实描述，不可说谎。"
    )
    for uid in players:
        uname = context.bot_data.get(uid, {}).get("name", f"玩家({uid})")
        await bot.send_message(
            chat_id,
            f"轮到 <a href='tg://user?id={uid}'>{uname}</a> 发言，请在30秒内完成描述。",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(20)
        await bot.send_message(chat_id, f"{uname} 剩下10秒！")
        await asyncio.sleep(10)

    await bot.send_message(chat_id, "所有玩家已描述完毕，下一阶段即将开始...")

async def view_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    word = game_state["player_words"].get(uid)
    if word is None:
        await query.answer("你不在游戏中。", show_alert=True)
    else:
        await query.answer(f"你的词语是：{'（空白）' if word == '' else word}", show_alert=True)

# 启动 bot
app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(entry_game, pattern="^game_werewolf$"))
app.add_handler(CallbackQueryHandler(set_mode, pattern="^mode_"))
app.add_handler(CallbackQueryHandler(join_game, pattern="^join_game$"))
app.add_handler(CallbackQueryHandler(view_word, pattern="^view_word$"))
app.run_polling()
