import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("酒鬼轮盘", callback_data="roulette")]]
    await update.message.reply_text(
        "开始游戏：请选择游戏模式",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def roulette_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    logger.info(f"启动倒计时，chat_id={chat_id}")
    await query.message.reply_text("酒鬼轮盘启动，倒计时60秒开始...")
    # ← 这里改用 context.application.job_queue
    context.application.job_queue.run_once(
        end_countdown,
        when=60,
        data={'chat_id': chat_id}
    )

async def end_countdown(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    chat_id = job.data['chat_id']
    logger.info(f"倒计时结束，发送测试文案 to {chat_id}")
    await context.bot.send_message(chat_id=chat_id, text="⏰ 倒计时测试成功！")

def main() -> None:
    app = ApplicationBuilder().token("7588230146:AAEMsvkdfptGr0CsYIO4L-ZEsPKlC7KH1K8").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(roulette_callback, pattern="^roulette$"))
    app.run_polling()

if __name__ == "__main__":
    main()
