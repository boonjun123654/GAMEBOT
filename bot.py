import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ChatMemberHandler

group_bombs = {}
group_selected = {}

WELCOME_IMAGE = "https://i.imgur.com/NJg6mjJ.jpeg"
RULE_IMAGE = "https://i.imgur.com/S8MjHnz.jpeg"
BOMB_IMAGE = "https://i.imgur.com/rZBrFTd.jpeg"
START_IMAGE = "https://i.imgur.com/WeYjoPN.jpeg"

async def welcome_on_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.my_chat_member and update.my_chat_member.new_chat_member.status == "member":
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=WELCOME_IMAGE,
            caption="欢迎使用💣TT炸弹数字小游戏！\n输入“开始游戏”马上开局！"
        )

async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_photo(
        photo=RULE_IMAGE,
        caption=(
            "🎯 游戏不限人数，建议 3-5 人\n\n"
            "1️⃣ 可用同一手机或多手机：\n"
            "▪️ 同一手机：传来传去点数字\n"
            "▪️ 多手机：各自点击群里按钮\n\n"
            "2️⃣ 每位玩家轮流点选数字\n"
            "💣 谁点中炸弹，谁就接受惩罚！"
        )
    )

def build_keyboard():
    keyboard = []
    row = []
    for i in range(1, 11):
        row.append(InlineKeyboardButton(str(i), callback_data=f"guess:{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def reset_game(chat_id):
    group_bombs[chat_id] = random.randint(1, 10)
    group_selected[chat_id] = set()

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await reset_game(chat_id)
    keyboard = build_keyboard()
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMAGE,
        caption="游戏开始！💣炸弹数字已准备！\n请根据顺序点选号码！",
        reply_markup=keyboard
    )

async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user = query.from_user.first_name
    selected = int(query.data.split(":")[1])

    if selected in group_selected.get(chat_id, set()):
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ 数字 {selected} 已被选过，请选别的！")
        return

    group_selected.setdefault(chat_id, set()).add(selected)
    await context.bot.send_message(chat_id=chat_id, text=f"🎯 {user} 选择了数字：{selected}")

    if selected == group_bombs.get(chat_id):
        restart_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 重新开始", callback_data="restart")]
        ])
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=BOMB_IMAGE,
            caption=f"💣Boom 炸弹爆炸啦！\n{user} 请接受惩罚！",
            reply_markup=restart_button
        )
        group_bombs.pop(chat_id, None)

async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start_game(query, context)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(ChatMemberHandler(welcome_on_added, chat_member_types=["my_chat_member"]))
    app.add_handler(CallbackQueryHandler(show_rules, pattern="^rules$"))
    app.add_handler(CallbackQueryHandler(handle_guess, pattern="^guess:\\d+$"))
    app.add_handler(CallbackQueryHandler(handle_restart, pattern="^restart$"))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(开始游戏|开始)$"), start_game))

    print("✅ Bot 正在运行...")
    app.run_polling()