import os
import logging
from datetime import datetime
from typing import Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

TOKEN = os.environ.get("TELEGRAM_TOKEN")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

candidates: Dict[str, int] = {}
user_votes: Dict[int, str] = {}

async def reset_daily(context: ContextTypes.DEFAULT_TYPE):
    candidates.clear()
    user_votes.clear()
    logger.info("每日重置完成")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 欢迎使用每日封号圈排行榜！\n\n"
        "/addcandidate 名字 - 添加候选人\n"
        "/vote 名字 - 投票\n"
        "/ranking - 查看排行榜\n"
        "/myvote - 查看我的投票\n\n"
        "每日0点自动重置！"
    )

async def add_candidate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法：/addcandidate 名字")
        return
    name = " ".join(context.args).strip()
    if name in candidates:
        await update.message.reply_text(f"⚠️「{name}」已存在！")
        return
    candidates[name] = 0
    await update.message.reply_text(f"✅ 已添加候选人：「{name}」")

async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("用法：/vote 名字")
        return
    name = " ".join(context.args).strip()
    if name not in candidates:
        await update.message.reply_text(f"❌ 没有「{name}」，请先 /addcandidate 添加")
        return
    prev = user_votes.get(user_id)
    if prev == name:
        await update.message.reply_text("⚠️ 你已投过这个人了")
        return
    if prev:
        candidates[prev] -= 1
    candidates[name] += 1
    user_votes[user_id] = name
    await update.message.reply_text(f"✅ 投票成功！你投给了「{name}」")

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not candidates:
        await update.message.reply_text("暂无候选人，用 /addcandidate 添加")
        return
    sorted_c = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    lines = ["🏆 今日封号圈排行榜\n"]
    for i, (name, votes) in enumerate(sorted_c, 1):
        lines.append(f"{i}. {name} —— {votes} 票")
    await update.message.reply_text("\n".join(lines))

async def my_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    v = user_votes.get(update.effective_user.id)
    if v:
        await update.message.reply_text(f"📌 你今天投给了「{v}」")
    else:
        await update.message.reply_text("你今天还没投票，用 /vote 参与吧！")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addcandidate", add_candidate))
    app.add_handler(CommandHandler("vote", vote))
    app.add_handler(CommandHandler("ranking", ranking))
    app.add_handler(CommandHandler("myvote", my_vote))
    app.job_queue.run_daily(reset_daily, time=datetime.strptime("00:00", "%H:%M").time())
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
