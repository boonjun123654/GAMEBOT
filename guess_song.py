
import json
import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# 加载歌曲库（统一一组，不分中文/粤语/福建）
with open("song_library_900_unique.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)
    SONG_LIST = raw_data
# 猜歌王主逻辑
async def handle_guess_song_callback(query, context):
    data = query.data

    if data == "game_guess_song":
        await query.message.edit_text(
            "🎤 《谁是猜歌王》\n\n你准备好了吗？",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("开始", callback_data="guess_song_start")]
            ])
        )

    elif data == "guess_song_start":
        song = random.choice(SONG_LIST)
        context.chat_data["current_song"] = song

        await query.message.edit_text(
            f"你抽到的歌曲是：\n🎵《{song['title']}》 — {song['artist']}\n\n"
            f"请在 30 秒内唱出副歌部分！"
        )

        await asyncio.sleep(10)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="成功唱出了吗？",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ 成功唱出", callback_data="guess_song_success"),
                 InlineKeyboardButton("💣 失败，请接受惩罚", callback_data="guess_song_fail")]
            ])
        )

    elif data == "guess_song_success":
        await query.message.edit_text(
            "太棒了！你成功通过挑战！🎉",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎲 再来一首", callback_data="guess_song_start")],
                [InlineKeyboardButton("🔙 切换游戏模式", callback_data="back_to_menu")]
            ])
        )

    elif data == "guess_song_fail":
        await query.message.edit_text(
            "哎呀～你没能唱出副歌！\n\n点击下方按钮进入惩罚轮盘，接受命运的挑战吧！🎡",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎯 进入惩罚轮盘", url="https://boonjun123654.github.io/punishment-task")],
                [InlineKeyboardButton("🎲 再来一首", callback_data="guess_song_start")],
                [InlineKeyboardButton("🔙 切换游戏模式", callback_data="back_to_menu")]
            ])
        )
