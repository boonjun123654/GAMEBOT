import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CallbackQueryHandler, filters

group_state = {}  # 记录每个群的炸弹数量和炸弹数字列表
group_selected = {}

START_IMAGE = "https://i.imgur.com/WeYjoPN.jpeg"
BOMB_IMAGE = "https://i.imgur.com/rZBrFTd.jpeg"

# 选择炸弹数量界面
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    group_state.pop(chat_id, None)
    group_selected.pop(chat_id, None)
    keyboard = [
        [
            InlineKeyboardButton("1 💣", callback_data="bombs:1"),
            InlineKeyboardButton("2 💣", callback_data="bombs:2"),
            InlineKeyboardButton("3 💣", callback_data="bombs:3")
        ]
    ]
    await context.bot.send_message(
        chat_id=chat_id,
        text="请选择本局💣的数量‼越多越刺激‼",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 初始化游戏
async def init_game(chat_id, bomb_count):
    bombs = random.sample(range(1, 11), k=bomb_count)
    group_state[chat_id] = bombs
    group_selected[chat_id] = set()

def build_keyboard(chat_id):
    keyboard = []
    row = []
    for i in range(1, 11):
        row.append(InlineKeyboardButton(str(i), callback_data=f"guess:{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    return InlineKeyboardMarkup(keyboard)

# 玩家选择炸弹数量
async def select_bomb_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    count = int(query.data.split(":")[1])
    await init_game(chat_id, count)
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMAGE,
        caption="游戏开始！💣炸弹数字已准备！\n请根据顺序点选号码！",
        reply_markup=build_keyboard(chat_id)
    )

# 玩家点击数字
async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    user = query.from_user.first_name
    data = query.data
    if chat_id not in group_state:
        await query.answer("游戏未启动", show_alert=True)
        return
    if not data.startswith("guess:"):
        return
    number = int(data.split(":")[1])
    if number in group_selected.get(chat_id, set()):
        await query.answer("这个数字已经被选过了！", show_alert=True)
        return
    group_selected[chat_id].add(number)
    await query.answer()
    await context.bot.send_message(chat_id=chat_id, text=f"{user} 选择了数字：{number}")
    if number in group_state.get(chat_id, []):
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=BOMB_IMAGE,
            caption=f"💣Boom 炸弹爆炸啦！\n{user} 请接受惩罚！",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 重新开始", callback_data="restart")]
            ])
        )
        group_state.pop(chat_id, None)
        group_selected.pop(chat_id, None)

# 重新开始按钮
async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start_game(query, context)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(开始游戏|开始)$"), start_game))
    app.add_handler(CallbackQueryHandler(select_bomb_count, pattern="^bombs:[1-3]$"))
    app.add_handler(CallbackQueryHandler(handle_guess, pattern="^guess:\\d+$"))
    app.add_handler(CallbackQueryHandler(handle_restart, pattern="^restart$"))

    print("✅ Bot 正在运行...")
    app.run_polling()