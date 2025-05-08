import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ChatMemberHandler

# 初始化全局炸弹数字
group_bombs = {}

# 欢迎图 URL（可换成你的图片链接）
WELCOME_IMAGE = "https://i.imgur.com/ybD6cJ7.png"
RULE_IMAGE = "https://i.imgur.com/tPU4MTY.png"
BOMB_IMAGE = "https://i.imgur.com/FMG5Lhv.png"
START_IMAGE = "https://i.imgur.com/tIHHwma.png"

# 被加入群组时自动发送欢迎信息
async def welcome_on_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.chat_member.new_chat_members:
        if member.id == context.bot.id:
            keyboard = [[InlineKeyboardButton("🎮 游戏规则", callback_data="rules")]]
            await context.bot.send_photo(
                chat_id=update.chat_member.chat.id,
                photo=WELCOME_IMAGE,
                caption="欢迎使用💣TT炸弹数字小游戏！\n输入“开始游戏”马上开局！",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

# 玩家点击“游戏规则”按钮
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

# 玩家输入“开始游戏”
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bomb_number = random.randint(1, 10)
    group_bombs[chat_id] = bomb_number

    keyboard = [[InlineKeyboardButton(str(i), callback_data=f"guess:{i}")] for i in range(1, 11)]
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMAGE,
        caption="游戏开始！💣炸弹数字已准备！\n请根据顺序点选号码！",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 玩家点了数字按钮
async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user = query.from_user.first_name
    selected = int(query.data.split(":")[1])
    bomb = group_bombs.get(chat_id, None)

    await context.bot.send_message(chat_id=chat_id, text=f"🎯 {user} 选择了数字：{selected}")

    if selected == bomb:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=BOMB_IMAGE,
            caption=f"💣Boom 炸弹爆炸啦！\n{user} 请接受惩罚！"
        )
        group_bombs.pop(chat_id, None)

# main 主函数
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(ChatMemberHandler(welcome_on_join, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CallbackQueryHandler(show_rules, pattern="^rules$"))
    app.add_handler(CallbackQueryHandler(handle_guess, pattern="^guess:\\d+$"))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(开始游戏|开始)$"), start_game))

    print("✅ Bot 正在运行...")
    app.run_polling()
