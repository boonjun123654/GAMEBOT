
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import asyncio
import random

# 游戏状态
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

# 示例词库
word_pairs = [
    ("沙发", "床"), ("苹果", "梨"), ("飞机", "火箭"),
    ("医生", "护士"), ("篮球", "排球"), ("电视", "显示器"),
    ("猫", "老虎"), ("火锅", "烧烤"), ("牛奶", "豆浆")
]

# 游戏入口：选择模式
async def entry_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("群组中进行", callback_data="werewolf:mode:group")],
        [InlineKeyboardButton("现实世界进行", callback_data="werewolf:mode:real")]
    ]
    await query.edit_message_text("请选择游戏模式：", reply_markup=InlineKeyboardMarkup(keyboard))

# 设置模式 + 开始报名
async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data.split(":")[-1]
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
    keyboard = [[InlineKeyboardButton("我要参加", callback_data="werewolf:join")]]
    await query.edit_message_text(
        f"🕹 模式已设定为：{mode}
请在 60 秒内点击下方按钮报名：",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.job_queue.run_once(end_registration, 60, data=query.message.chat_id)

# 玩家点击参加
async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    uname = query.from_user.full_name
    await query.answer("你已报名！", show_alert=True)
    if uid not in game_state["players"]:
        game_state["players"].append(uid)
        context.bot_data[uid] = {"name": uname}
    keyboard = [[InlineKeyboardButton("我要参加", callback_data="werewolf:join")]]
    await query.edit_message_text(
        f"当前已报名人数：{len(game_state['players'])}
点击继续加入（剩余时间内）",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 查看词语按钮
async def view_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    word = game_state["player_words"].get(uid)
    if word is None:
        await query.answer("你不在游戏中。", show_alert=True)
    else:
        await query.answer(f"你的词语是：{'（空白）' if word == '' else word}", show_alert=True)

# 报名结束 → 发词
async def end_registration(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    bot = context.bot
    players = game_state["players"]

    if len(players) < 4:
        await bot.send_message(chat_id, "❌ 人数不足，游戏取消。")
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
        btn = [[InlineKeyboardButton("查看我的词语", callback_data="werewolf:view")]]
        await bot.send_message(uid, "如需再次查看，请点击：", reply_markup=InlineKeyboardMarkup(btn))

    await bot.send_message(chat_id, "🎮 游戏开始！词语已发出，请准备描述。")
    await start_description_phase(chat_id, context)

# 描述阶段
async def start_description_phase(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    players = game_state["players"]
    await bot.send_message(
        chat_id,
        "🗣 描述阶段开始！请每位玩家用一句话描述你的词语。
⚠️ 请真实描述，不可说谎。"
    )
    for uid in players:
        uname = context.bot_data.get(uid, {}).get("name", f"玩家({uid})")
        await bot.send_message(
            chat_id,
            f"🎤 <a href='tg://user?id={uid}'>{uname}</a>，请在 30 秒内发言。",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(20)
        await bot.send_message(chat_id, f"⏳ {uname} 剩下 10 秒！")
        await asyncio.sleep(10)

    await bot.send_message(chat_id, "✅ 所有玩家已描述完毕，下一阶段即将开始...")

# 导出函数供 bot.py 使用
__all__ = [
    "entry_game",
    "set_mode",
    "join_game",
    "view_word",
    "game_state"
]

# 投票记录
votes = {}            # uid: voted_uid
eliminated = set()    # 被淘汰玩家

# 启动投票阶段
async def start_vote_phase(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    votes.clear()
    await bot.send_message(chat_id, "🗳 投票时间到！请点选你认为是卧底的玩家👇")

    # 投票按钮（仅限未淘汰玩家）
    keyboard = []
    for uid in game_state["players"]:
        if uid in eliminated:
            continue
        uname = context.bot_data.get(uid, {}).get("name", str(uid))
        keyboard.append([InlineKeyboardButton(uname, callback_data=f"werewolf:vote:{uid}")])

    await bot.send_message(chat_id, "请点击以下玩家名字投票：", reply_markup=InlineKeyboardMarkup(keyboard))

# 接收投票操作
async def handle_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    voter = query.from_user.id
    voted_uid = int(query.data.split(":")[-1])

    if voter not in game_state["players"] or voter in eliminated:
        await query.answer("你已被淘汰，无法投票！", show_alert=True)
        return
    if voter in votes:
        await query.answer("你已投过票了！", show_alert=True)
        return

    votes[voter] = voted_uid
    await query.answer("✅ 投票成功！", show_alert=True)

    # 所有人投完就统计结果
    active_voters = [uid for uid in game_state["players"] if uid not in eliminated]
    if len(votes) == len(active_voters):
        await count_votes_and_check(query.message.chat_id, context)

# 投票结果统计 + 胜负判断
async def count_votes_and_check(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot

    # 统计票数
    count = {}
    for uid in votes.values():
        count[uid] = count.get(uid, 0) + 1

    max_votes = max(count.values())
    top = [uid for uid, v in count.items() if v == max_votes]

    if len(top) > 1:
        await bot.send_message(chat_id, "⚠️ 出现平票！进入第二轮仅限平票玩家描述")
        await second_round(chat_id, context, top)
        return

    # 淘汰玩家
    eliminated_uid = top[0]
    eliminated.add(eliminated_uid)
    uname = context.bot_data.get(eliminated_uid, {}).get("name", str(eliminated_uid))
    await bot.send_message(chat_id, f"🪦 玩家 {uname} 被淘汰！")

    # 胜负判断
    if eliminated_uid == game_state["undercover"]:
        await bot.send_message(chat_id, "🎉 卧底被票出，平民胜利！")
        await reveal_result(chat_id, context)
    elif eliminated_uid == game_state["whiteboard"]:
        await bot.send_message(chat_id, "白板出局，游戏继续！")
        await start_description_phase(chat_id, context)
    else:
        survivors = [uid for uid in game_state["players"] if uid not in eliminated]
        if len(survivors) <= 2 and game_state["undercover"] in survivors:
            await bot.send_message(chat_id, "😈 卧底成功潜伏到最后，卧底胜利！")
            await reveal_result(chat_id, context)
        else:
            await start_description_phase(chat_id, context)

# 第二轮描述 + 投票（平票处理）
async def second_round(chat_id: int, context: ContextTypes.DEFAULT_TYPE, tied_players: list):
    bot = context.bot
    await bot.send_message(chat_id, "🎤 平票玩家开始 30 秒发言时间...")

    for uid in tied_players:
        uname = context.bot_data.get(uid, {}).get("name", str(uid))
        await bot.send_message(chat_id, f"请 <a href='tg://user?id={uid}'>{uname}</a> 发言", parse_mode=ParseMode.HTML)
        await asyncio.sleep(20)
        await bot.send_message(chat_id, f"{uname} 剩下 10 秒...")
        await asyncio.sleep(10)

    # 二轮投票
    global votes
    votes.clear()
    keyboard = []
    for uid in tied_players:
        uname = context.bot_data.get(uid, {}).get("name", str(uid))
        keyboard.append([InlineKeyboardButton(uname, callback_data=f"werewolf:vote2:{uid}")])
    await bot.send_message(chat_id, "🔁 第二轮投票开始！", reply_markup=InlineKeyboardMarkup(keyboard))

# 第二轮投票逻辑
async def handle_vote2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    voter = query.from_user.id
    voted_uid = int(query.data.split(":")[-1])

    if voter not in game_state["players"] or voter in eliminated:
        await query.answer("你已被淘汰，无法投票！", show_alert=True)
        return
    if voter in votes:
        await query.answer("你已投过票了！", show_alert=True)
        return

    votes[voter] = voted_uid
    await query.answer("✅ 投票成功！", show_alert=True)

    tied_players = [uid for uid in votes.values()]
    if len(votes) == len([uid for uid in game_state["players"] if uid not in eliminated]):
        # 判断是否再次平票
        result = {}
        for uid in votes.values():
            result[uid] = result.get(uid, 0) + 1
        top = [uid for uid, v in result.items() if v == max(result.values())]
        if len(top) > 1:
            for uid in top:
                eliminated.add(uid)
            await context.bot.send_message(query.message.chat.id, "⚔️ 第二轮仍平票，平票玩家全部淘汰！")
        else:
            eliminated.add(top[0])
            uname = context.bot_data.get(top[0], {}).get("name", str(top[0]))
            await context.bot.send_message(query.message.chat.id, f"🪦 玩家 {uname} 被淘汰！")
        await start_description_phase(query.message.chat.id, context)

# 公布身份与重启按钮
async def reveal_result(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = "🎯 本局词语：
"
    msg += f"▪️ 平民词：{game_state['word_pair'][0]}
"
    msg += f"▪️ 卧底词：{game_state['word_pair'][1]}

"
    msg += "👥 玩家身份：
"
    for uid in game_state["players"]:
        role = "卧底" if uid == game_state["undercover"] else "白板" if uid == game_state["whiteboard"] else "平民"
        name = context.bot_data.get(uid, {}).get("name", str(uid))
        msg += f"- {name}：{role}
"

    await bot.send_message(chat_id, msg, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 重新开始", callback_data="werewolf:restart")],
        [InlineKeyboardButton("🎮 切换游戏模式", callback_data="mainmenu")]
    ]))

async def start_game_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    # 重置数据
    game_state.update({
        "players": [],
        "player_words": {},
        "undercover": None,
        "whiteboard": None,
        "word_pair": ("", ""),
        "status": "registering",
        "chat_id": chat_id
    })
    eliminated.clear()
    votes.clear()

    keyboard = [[InlineKeyboardButton("我要参加", callback_data="werewolf:join")]]
    await context.bot.send_message(
        chat_id=chat_id,
        text="新一轮《谁是卧底》开始报名啦！请点击下方按钮加入 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.job_queue.run_once(end_registration, 60, data=chat_id)

