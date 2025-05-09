from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# 在开始 WenChi 游戏时，确保 group_data[chat_id] 是字典结构
async def start_wenchi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    group_data[chat_id] = {
        "bad": random.randint(1, 10),
        "selected": [],
        "mode": "wenchi"
    }
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMAGE,
        caption="😋WenChi 今天吃什么？\n请从以下选项中选择一道菜！",
        reply_markup=wenchi_keyboard()
    )

# 在猜测时使用 get() 不会报错
async def handle_wenchi_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user = query.from_user.first_name

    choice = int(query.data.split("_")[-1])
    game = group_data.get(chat_id, {})

    if choice in game.get("selected", []):
        await query.answer("这个食物已经被选过啦！", show_alert=True)
        return

    game["selected"].append(choice)

    if choice == game.get("bad"):
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=WENCHI_FAIL_IMAGE,
            caption=f"Oh no！WenChi吃坏肚子了！\n{user} 选中了泻肚子的食物！",
            reply_markup=restart_keyboard()
        )
        group_data.pop(chat_id, None)
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{user} 选择了 {choice}，还好没事！"
        )
