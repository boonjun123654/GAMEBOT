
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, ContextTypes, MessageHandler, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("测试 Bot 已启动，60 秒后将触发任务！")
    context.job_queue.run_once(job_trigger_test, 60, data=chat_id)

async def job_trigger_test(context: CallbackContext):
    chat_id = context.job.data
    await context.bot.send_message(chat_id=chat_id, text="✅ 倒计时测试成功！这是 60 秒后的触发消息。")

if __name__ == '__main__':
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(开始游戏)$"), start))

    job_queue = app.job_queue  # 确保 JobQueue 初始化
    print("✅ 测试版 JobQueue 倒计时 Bot 已运行")
    app.run_polling()
