from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
import os
import re
from datetime import datetime
from collections import Counter
import pandas as pd
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

# Загружаем токен из .env файла
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

FILE_NAME = "mood_diary.xlsx"

# Проверяем, есть ли таблица — если нет, создаём
if not os.path.exists(FILE_NAME):
    columns = [
        "Дата/время", "Пользователь", "Место", "Событие", "Автоматическая мысль",
        "Эмоции", "Физические ощущения", "Поведение",
        "Факты подтверждающие идею", "Факты против идеи",
        "Если мысль верна — самое плохое, смогу ли пережить?",
        "Если мысль верна — самое хорошее?",
        "Какой вариант реалистичный?",
        "Что бы я посоветовал другу?",
        "Если буду думать также — что будет с эмоциями?",
        "Что я должен(должна) делать?",
        "Новая автоматическая мысль"
    ]
    pd.DataFrame(columns=columns).to_excel(FILE_NAME, index=False)

# Состояния диалога
PLACE, EVENT, THOUGHT, EMOTIONS, PHYS, BEHAVIOR, FACTS_FOR, FACTS_AGAINST, BAD, GOOD, REALISTIC, ADVICE, EFFECT, ACTION, NEW_THOUGHT = range(15)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало заполнения дневника"""
    await update.message.reply_text("📍 Где ты сейчас находишься?")
    return PLACE

async def get_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Место"] = update.message.text
    await update.message.reply_text("✨ Что случилось? (опиши событие)")
    return EVENT

async def get_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Событие"] = update.message.text
    await update.message.reply_text("💭 Какая у тебя автоматическая мысль?")
    return THOUGHT

async def get_thought(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Автоматическая мысль"] = update.message.text
    await update.message.reply_text("😊 Какие эмоции ты чувствуешь?")
    return EMOTIONS

async def get_emotions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Эмоции"] = update.message.text
    await update.message.reply_text("💪 Какие физические ощущения?")
    return PHYS

async def get_phys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Физические ощущения"] = update.message.text
    await update.message.reply_text("🤔 Как ты себя повёл(а)?")
    return BEHAVIOR

async def get_behavior(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Поведение"] = update.message.text
    await update.message.reply_text("📚 Какие факты подтверждают эту идею?")
    return FACTS_FOR

async def get_facts_for(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Факты подтверждающие идею"] = update.message.text
    await update.message.reply_text("⚖️ Какие факты против этой идеи?")
    return FACTS_AGAINST

async def get_facts_against(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Факты против идеи"] = update.message.text
    await update.message.reply_text("😟 Если мысль верна, что самое плохое может случиться, сможешь ли ты это пережить?")
    return BAD

async def get_bad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Если мысль верна — самое плохое, смогу ли пережить?"] = update.message.text
    await update.message.reply_text("🌤 Если мысль верна, что самое хорошее может случиться?")
    return GOOD

async def get_good(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Если мысль верна — самое хорошее?"] = update.message.text
    await update.message.reply_text("⚖️ Какой вариант развития событий между плохим и хорошим самый реалистичный?")
    return REALISTIC

async def get_realistic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Какой вариант реалистичный?"] = update.message.text
    await update.message.reply_text("👭 Если бы твоя подруга/друг думали так же, что бы ты им посоветовал?")
    return ADVICE

async def get_advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Что бы я посоветовал другу?"] = update.message.text
    await update.message.reply_text("💭 Если ты продолжишь думать так же, что будет с твоими эмоциями?")
    return EFFECT

async def get_effect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Если буду думать также — что будет с эмоциями?"] = update.message.text
    await update.message.reply_text("🧭 Что ты тогда должен(должна) делать?")
    return ACTION

async def get_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Что я должен(должна) делать?"] = update.message.text
    await update.message.reply_text("🌱 Какая теперь у тебя новая автоматическая мысль?")
    return NEW_THOUGHT

async def get_new_thought(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Новая автоматическая мысль"] = update.message.text

    user = update.message.from_user
    user_name = f"{user.first_name} {user.last_name or ''}".strip()

    df = pd.read_excel(FILE_NAME)
    new_entry = {
        "Дата/время": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Пользователь": user_name,
        **context.user_data
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_excel(FILE_NAME, index=False)

    await update.message.reply_text("✅ Запись добавлена в дневник! Спасибо 💖")
    context.user_data.clear()
    return ConversationHandler.END

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет Excel файл"""
    if os.path.exists(FILE_NAME):
        await update.message.reply_document(open(FILE_NAME, "rb"))
    else:
        await update.message.reply_text("📂 Файл дневника пока не создан.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику пользователя"""
    user = update.message.from_user
    user_name = f"{user.first_name} {user.last_name or ''}".strip()

    if not os.path.exists(FILE_NAME):
        await update.message.reply_text("📂 Пока нет данных для анализа.")
        return

    df = pd.read_excel(FILE_NAME)
    user_entries = df[df["Пользователь"] == user_name]

    if user_entries.empty:
        await update.message.reply_text("📝 У тебя пока нет записей в дневнике.")
        return

    total = len(user_entries)
    first_date = user_entries["Дата/время"].iloc[0]
    last_date = user_entries["Дата/время"].iloc[-1]

    all_emotions = " ".join(str(e).lower() for e in user_entries["Эмоции"])
    words = re.findall(r"\w+", all_emotions)
    common_emotions = Counter(words).most_common(5)

    if common_emotions:
        emotion_text = "\n".join([f"• {e[0]} — {e[1]} раз(а)" for e in common_emotions])
    else:
        emotion_text = "Нет данных об эмоциях."

    msg = (
        f"📈 *Твоя статистика настроений:*\n\n"
        f"Всего записей: {total}\n"
        f"Период: с {first_date} по {last_date}\n\n"
        f"💬 *Чаще всего упоминаемые эмоции:*\n{emotion_text}"
    )

    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_place)],
            EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_event)],
            THOUGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_thought)],
            EMOTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_emotions)],
            PHYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phys)],
            BEHAVIOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_behavior)],
            FACTS_FOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_facts_for)],
            FACTS_AGAINST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_facts_against)],
            BAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_bad)],
            GOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_good)],
            REALISTIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_realistic)],
            ADVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_advice)],
            EFFECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_effect)],
            ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_action)],
            NEW_THOUGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_thought)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("export", export))
    app.add_handler(CommandHandler("stats", stats))

    print("🤖 Бот запущен... Нажми Ctrl+C чтобы остановить.")
    app.run_polling()

if __name__ == "__main__":
    main()
