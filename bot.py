# bot.py
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ChatMemberHandler, ContextTypes, filters,
)
import os

BOT_TOKEN = os.getenv("8034990761:AAEOAsRNSQYc1VcFqRxdEsd4oUfqSjMMXFE")
games = {}

async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.my_chat_member.new_chat_member.status == 'member':
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id=chat_id,
            text="欢迎使用💣TT炸弹小游戏！\n输入“开始游戏”马上开局！",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 游戏规则", callback_data="rules")]])
        )

async def rules_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "游戏不限人数，3-5人为佳\n\n"
        "1 - 使用同一架手机 / 多架手机都可以\n"
        "▪️ 一架手机：玩家传递手机点选数字\n"
        "▪️ 多架手机：玩家在各自手机点选数字\n\n"
        "2 - 每位玩家轮流点选数字，选中炸弹会自动发布结果"
    )

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if text != "开始游戏":
        return

    bomb = random.randint(1, 10)
    games[chat_id] = {"bomb": bomb, "guessed": [], "active": True}

    buttons = [
        [InlineKeyboardButton(str(i), callback_data=f"guess_{i}")]
        for i in range(1, 11)
    ]
    await update.message.reply_text(
        "游戏开始！💣炸弹数字已准备！\n\n请根据顺序点选号码！",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id
    username = user.mention_html()

    if chat_id not in games or not games[chat_id]["active"]:
        await query.answer("游戏未开始或已结束")
        return

    guess = int(query.data.split("_")[1])
    if guess in games[chat_id]["guessed"]:
        await query.answer("这个数字已经被选过了！", show_alert=True)
        return

    games[chat_id]["guessed"].append(guess)

    if guess == games[chat_id]["bomb"]:
        games[chat_id]["active"] = False
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"💣Bomb 炸弹爆炸啦！\n\n{username} 请接受惩罚！",
            parse_mode="HTML"
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{username} 选择了数字 {guess}，安全！",
            parse_mode="HTML"
        )

    await query.answer()

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatMemberHandler(welcome_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, start_game))
    app.add_handler(CallbackQueryHandler(rules_callback, pattern="^rules$"))
    app.add_handler(CallbackQueryHandler(handle_guess, pattern="^guess_"))
    print("Bot 已启动")
    app.run_polling()

if __name__ == "__main__":
    main()
