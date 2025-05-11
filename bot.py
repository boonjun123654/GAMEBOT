import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CallbackContext,
    CommandHandler, CallbackQueryHandler
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
group_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 请选择游戏模式：",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🤤 酒鬼轮盘", callback_data="mode:wheel")]
        ])
    )

async def handle_mode_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    await context.bot.send_message(chat_id=chat_id, text="🥃 酒鬼轮盘选择成功，60 秒倒计时开始...")
    
    # 启动倒计时任务
    context.job_queue.run_once(job_trigger_test, 60, data=chat_id)

def job_trigger_test(context: CallbackContext):
    chat_id = context.job.data
    asyncio.create_task(context.bot.send_message(chat_id=chat_id, text="✅ 倒计时测试成功！已触发 JobQueue 任务。"))

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_mode_select, pattern="^mode:wheel$"))
    print("✅ 测试 Bot 已启动")
    app.run_polling()