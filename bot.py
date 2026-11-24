import html
import logging
import os
from urllib.parse import quote_plus

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

import mood_model
from quiz import MOOD_INFO, MOODS, QUESTIONS, RECOMMENDATION_QUESTIONS
from recommender import recommend

TEST_QUESTIONS = QUESTIONS + RECOMMENDATION_QUESTIONS

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("musica-mood-bot")

TOKEN = os.getenv("TELEGRAM_TOKEN")

# ─── Teclados ───────────────────────────────────────────────

def kb_start():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🎧 Empezar el test", callback_data="start")]])


def kb_question(qi):
    rows = [
        [InlineKeyboardButton(label, callback_data=f"a:{qi}:{ai}")]
        for ai, (label, _) in enumerate(TEST_QUESTIONS[qi]["options"])
    ]
    return InlineKeyboardMarkup(rows)


def kb_results(mood, uplift):
    rows = [[InlineKeyboardButton("🔄 Más canciones", callback_data="more")]]
    if mood == "melancolico" and not uplift:
        rows.append([InlineKeyboardButton("🌤️ Quiero animarme", callback_data="uplift")])
    rows.append([InlineKeyboardButton("📝 Repetir el test", callback_data="start")])
    return InlineKeyboardMarkup(rows)


def kb_feedback():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Sí, acertó", callback_data="fb:yes"),
        InlineKeyboardButton("❌ No", callback_data="fb:no"),
    ]])


def kb_true_mood():
    rows, row = [], []
    for m in MOODS:
        emoji, name, _ = MOOD_INFO[m]
        row.append(InlineKeyboardButton(f"{emoji} {name}", callback_data=f"t:{m}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)

# ─── Textos ─────────────────────────────────────────────────

def question_text(qi):
    return f"<b>Pregunta {qi + 1}/{len(TEST_QUESTIONS)}</b>\n\n{html.escape(TEST_QUESTIONS[qi]['text'])}"


def song_line(i, s):
    q = quote_plus(f"{s['title']} {s['artist']}")
    return (
        f"{i}. <b>{html.escape(s['title'])}</b> — {html.escape(s['artist'])}\n"
        f"    <a href=\"https://www.youtube.com/results?search_query={q}\">▶️ YouTube</a>"
        f" · <a href=\"https://open.spotify.com/search/{q}\">🟢 Spotify</a>"
    )


def results_text(detected, ranked, target, songs, uplift):
    emoji, name, desc = MOOD_INFO[detected]
    pct = dict(ranked)[detected]
    head = f"{emoji} <b>Tu mood: {name}</b> ({pct:.0%})\n<i>{html.escape(desc)}</i>\n"
    second, p2 = ranked[1]
    if p2 >= 0.2:
        e2, n2, _ = MOOD_INFO[second]
        head += f"También hay algo de {e2} {n2} ({p2:.0%}).\n"
    if uplift:
        head += "\n🌤️ <b>Para subirte el ánimo poquito a poco:</b>\n"
    elif target == "estresado":
        head += "\n🌿 <b>Para bajar revoluciones:</b>\n"
    else:
        head += "\n🎶 <b>Tu playlist para este momento:</b>\n"
    body = "\n".join(song_line(i, s) for i, s in enumerate(songs, 1))
    return f"{head}\n{body}"

# ─── Utilidades ─────────────────────────────────────────────

async def safe_edit(query, text, markup=None):
    try:
        await query.edit_message_text(
            text, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True
        )
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            raise


async def show_songs(query, context, target, uplift=False, new_batch=True):
    ud = context.user_data
    shown = ud.setdefault("shown", set()) if new_batch else set()
    songs = recommend(target, n=5, exclude=shown, **ud["preferences"])
    shown.update(s["idx"] for s in songs)
    ud["shown"] = shown
    ud["view"] = {"target": target, "uplift": uplift}
    text = results_text(ud["mood"], ud["ranked"], target, songs, uplift)
    await safe_edit(query, text, kb_results(ud["mood"], uplift))

# ─── Comandos ───────────────────────────────────────────────

WELCOME = (
    "👋 ¡Hola! Estoy aquí para ponerte la banda sonora de este momento.\n\n"
    f"Responde <b>{len(TEST_QUESTIONS)} preguntas rápidas</b> y descubriré tu mood con un toque de "
    "inteligencia artificial. Después elegiré canciones que encajen contigo.\n\n"
    "🌦️ Sin juicios. Solo música para cómo estás hoy."
)

HELP_TEXT = (
    "🎧 <b>Cómo puedo ayudarte</b>\n\n"
    "• /test — descubre tu estado de ánimo\n"
    "• /cancel — cancela el test actual\n"
    "• 🔄 Más canciones — cambia algunas recomendaciones\n"
    "• 🌤️ Quiero animarme — usa un perfil más alegre\n"
    "• Feedback — me ayuda a aprender para la próxima vez"
)


async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Presentarme"),
        BotCommand("test", "Descubrir mi mood"),
        BotCommand("cancel", "Cancelar el test"),
        BotCommand("help", "Ver ayuda"),
    ])
    await application.bot.set_my_description(
        "Tu acompañante musical: descubre tu estado de ánimo y encuentra canciones para este momento."
    )
    await application.bot.set_my_short_description(
        "Música personalizada según cómo te sientes."
    )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(WELCOME, parse_mode="HTML", reply_markup=kb_start())


async def cmd_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["answers"] = []
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(question_text(0), parse_mode="HTML", reply_markup=kb_question(0))


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(
        "Test cancelado. Cuando quieras volver, pulsa /test. Aquí estaré. 💚",
        parse_mode="HTML",
        reply_markup=kb_start(),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML")

# ─── Callbacks ──────────────────────────────────────────────

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    ud = context.user_data

    if data == "start":
        ud.clear()
        ud["answers"] = []
        await safe_edit(query, question_text(0), kb_question(0))

    elif data.startswith("a:"):
        _, qi, ai = data.split(":")
        qi, ai = int(qi), int(ai)
        answers = ud.get("answers")
        if (
            answers is None
            or len(answers) != qi
            or not 0 <= qi < len(TEST_QUESTIONS)
            or not 0 <= ai < len(TEST_QUESTIONS[qi]["options"])
        ):
            await safe_edit(query, "Ese test ya no está activo. ¿Empezamos de nuevo?", kb_start())
            return
        answers.append(ai)
        if qi + 1 < len(TEST_QUESTIONS):
            await safe_edit(query, question_text(qi + 1), kb_question(qi + 1))
            return
        # Test terminado -> predicción
        mood_answers = answers[:len(QUESTIONS)]
        ud["preferences"] = {
            key: question["options"][answer][1]
            for key, question, answer in zip(
                ("activity", "excluded_genre"), RECOMMENDATION_QUESTIONS, answers[len(QUESTIONS):]
            )
        }
        ranked = mood_model.predict(mood_answers)
        ud["ranked"] = ranked
        ud["mood"] = ranked[0][0]
        ud["final_answers"] = mood_answers
        ud["shown"] = set()
        await show_songs(query, context, ud["mood"])
        await query.message.reply_text(
            "¿Acerté con tu estado de ánimo? Tu respuesta ayuda a mejorar el modelo 🙌",
            reply_markup=kb_feedback(),
        )

    elif data == "more" and "mood" in ud:
        view = ud.get("view", {"target": ud["mood"], "uplift": False})
        await show_songs(query, context, view["target"], view["uplift"])

    elif data == "uplift" and "mood" in ud:
        ud["shown"] = set()
        await show_songs(query, context, "feliz", uplift=True)

    elif data == "fb:yes" and "final_answers" in ud:
        mood_model.save_feedback(ud["final_answers"], ud["mood"])
        await query.edit_message_text("¡Gracias! 💚 Quedó guardado para mejorar el modelo.")

    elif data == "fb:no" and "final_answers" in ud:
        await query.edit_message_text("¡Ups! ¿Cómo te sentías en realidad?", reply_markup=kb_true_mood())

    elif data.startswith("t:") and "final_answers" in ud:
        true_mood = data.split(":")[1]
        if true_mood in MOODS:
            mood_model.save_feedback(ud["final_answers"], true_mood)
            emoji, name, _ = MOOD_INFO[true_mood]
            songs = recommend(true_mood, n=5, **ud["preferences"])
            text = (
                f"Gracias, lo anoté para aprender. {emoji} <b>{name}</b> entonces. "
                f"Aquí van canciones para ese mood:\n\n"
                + "\n".join(song_line(i, s) for i, s in enumerate(songs, 1))
            )
            await safe_edit(query, text)

    else:
        await safe_edit(query, "Ese botón ya no está activo. ¿Hacemos el test?", kb_start())

# ─── Main ───────────────────────────────────────────────────

def main():
    if not TOKEN:
        raise SystemExit(
            "❌ Falta TELEGRAM_TOKEN. Crea un archivo .env con TELEGRAM_TOKEN=... "
            "(ver .env.example) o exporta la variable de entorno."
        )
    mood_model.get_model()  # carga o entrena el modelo al iniciar
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler(["ayuda", "help"], cmd_help))
    app.add_handler(CommandHandler("test", cmd_test))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CallbackQueryHandler(on_callback))
    log.info("🟢 Bot corriendo... Esperando mensajes")
    app.run_polling()


if __name__ == "__main__":
    main()
