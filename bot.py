import asyncio
import html
import io
import logging
from datetime import datetime, timezone
from aiohttp import web
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Sample dummy records for testing UI & .txt export (no real personal data)
SAMPLE_RECORDS = {
    "7070230385": [
        {
            "name": "Sample Record One",
            "parent": "Sample Parent",
            "number": "7070230385",
            "address": "Sample Street, Demo City, 000000",
            "circle": "DEMO CIRCLE",
            "alternate": "Not Available",
            "id_ref": "DEMO-ID-001",
        },
        {
            "name": "Sample Record Two",
            "parent": "Sample Parent",
            "number": "7070230385",
            "address": "Sample Street, Demo City, 000000",
            "circle": "DEMO CIRCLE",
            "alternate": "Not Available",
            "id_ref": "DEMO-ID-002",
        },
    ]
}

MAIN_REPLY_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["📖 ɪɴᴛʀᴏᴅᴜᴄᴛɪᴏɴ", "🔢 ɴᴜᴍʙᴇʀ ɪɴꜰᴏ"],
        ["📜 ʜᴇʟᴘ & ɢᴜɪᴅᴇ", "📞 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ"],
    ],
    resize_keyboard=True,
)


def get_inline_links() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔕 𝗨𝗽𝗱𝗮𝘁𝗲 🔕", url=config.UPDATE_CHANNEL),
                InlineKeyboardButton("💌 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 💌", url=config.SUPPORT_GROUP),
            ],
            [
                InlineKeyboardButton("📖 ʜᴇʟᴘ ɢᴜɪᴅᴇ", callback_data="help_menu"),
                InlineKeyboardButton("🔢 ᴜꜱᴀɢᴇ", callback_data="usage_guide"),
            ],
        ]
    )


async def send_log(context: ContextTypes.DEFAULT_TYPE, log_text: str) -> None:
    if not config.LOG_GROUP_ID:
        return
    try:
        await context.bot.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=log_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception as exc:
        logger.warning("Failed to send log to %s: %s", config.LOG_GROUP_ID, exc)


def format_user_tag(update: Update) -> str:
    user = update.effective_user
    if not user:
        return "Unknown User"
    full_name = html.escape(user.full_name or "User")
    username = f"@{user.username}" if user.username else "No Username"
    return f"<a href='tg://user?id={user.id}'>{full_name}</a> (<code>{user.id}</code> | {username})"


# ──────────────────── COMMANDS ──────────────────── #


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    mention = f"<a href='tg://user?id={user.id}'>{html.escape(user.first_name)}</a>"

    caption = (
        "✨ <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ ʀᴏʙᴏᴛ</b> ✨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 <b>ʜᴇʟʟᴏ</b> {mention}!\n\n"
        "⚡ <b>ꜰᴇᴀᴛᴜʀᴇꜱ:</b>\n"
        "• ɪɴꜱᴛᴀɴᴛ ꜰᴏʀᴍᴀᴛᴛᴇᴅ ʟᴏᴏᴋᴜᴘ ᴄᴀʀᴅꜱ\n"
        "• ᴀᴜᴛᴏᴍᴀᴛɪᴄ <code>.txt</code> ʀᴇᴘᴏʀᴛ ᴇxᴘᴏʀᴛ\n"
        "• ꜰᴀꜱᴛ, ᴄʀᴇᴅɪᴛ-ꜰʀᴇᴇ ᴅɪʀᴇᴄᴛ ᴀᴄᴄᴇꜱꜱ\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 <b>ᴏᴡɴᴇʀ:</b> {config.OWNER_USERNAME}\n"
        f"🤖 <b>ʙᴏᴛ:</b> {config.BOT_USERNAME}"
    )

    try:
        await update.message.reply_photo(
            photo=config.START_IMG,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=get_inline_links(),
        )
    except Exception as exc:
        logger.warning("Start photo failed, sending text fallback: %s", exc)
        await update.message.reply_text(
            caption,
            parse_mode=ParseMode.HTML,
            reply_markup=get_inline_links(),
        )

    await update.message.reply_text(
        "👇 <b>ᴄʜᴏᴏꜱᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ꜰʀᴏᴍ ᴛʜᴇ ᴍᴇɴᴜ ʙᴇʟᴏᴡ:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=MAIN_REPLY_KEYBOARD,
    )

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    await send_log(
        context,
        "🚀 <b>#NEW_START</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>ᴜꜱᴇʀ:</b> {format_user_tag(update)}\n"
        f"🕒 <b>ᴛɪᴍᴇ:</b> <code>{now_utc}</code>",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📜 <b>ʜᴇʟᴘ &amp; ᴄᴏᴍᴍᴀɴᴅ ɢᴜɪᴅᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 <code>/start</code> — ᴏᴘᴇɴ ᴍᴀɪɴ ᴍᴇɴᴜ &amp; ʙᴀɴɴᴇʀ\n"
        "🔹 <code>/num &lt;number&gt;</code> — ɢᴇɴᴇʀᴀᴛᴇ ʟᴏᴏᴋᴜᴘ ʀᴇᴘᴏʀᴛ + <code>.txt</code>\n"
        "🔹 <code>/help</code> — ᴠɪᴇᴡ ᴛʜɪꜱ ɢᴜɪᴅᴇ\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
        "<code>/num 7070230385</code>\n\n"
        f"👨‍💻 <b>ᴅᴇᴠ:</b> {config.OWNER_USERNAME}"
    )
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_inline_links(),
    )


def build_report(query_num: str, records: list[dict]) -> str:
    safe_query = html.escape(query_num)
    lines = [
        "🔎 <b>ɴᴜᴍʙᴇʀ ʟᴏᴏᴋᴜᴘ ʀᴇꜱᴜʟᴛ</b>",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🔢 <b>ꜱᴇᴀʀᴄʜᴇᴅ ɴᴜᴍʙᴇʀ :</b> <code>{safe_query}</code>",
        f"📊 <b>ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ :</b> <code>{len(records)}</code>",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
    ]

    for idx, rec in enumerate(records, start=1):
        lines.extend([
            f"👤 <b>ʀᴇᴄᴏʀᴅ {idx}</b>",
            f"🟡 <b>ɴᴀᴍᴇ :</b> {html.escape(rec['name'])}",
            f"🪪 <b>ᴘᴀʀᴇɴᴛ ɴᴀᴍᴇ :</b> {html.escape(rec['parent'])}",
            f"📱 <b>ᴍᴏʙɪʟᴇ :</b> <code>{html.escape(rec['number'])}</code>",
            f"📍 <b>ᴀᴅᴅʀᴇꜱꜱ :</b> {html.escape(rec['address'])}",
            f"📡 <b>ᴄɪʀᴄʟᴇ :</b> {html.escape(rec['circle'])}",
            f"🔄 <b>ᴀʟᴛᴇʀɴᴀᴛᴇ :</b> {html.escape(rec['alternate'])}",
            f"🆔 <b>ɪᴅ ʀᴇꜰ :</b> <code>{html.escape(rec['id_ref'])}</code>",
            "━━━━━━━━━━━━━━━━━━━━",
            "",
        ])

    if not records:
        lines.extend(["⚠️ <i>ɴᴏ ꜱᴀᴍᴘʟᴇ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ ꜰᴏʀ ᴛʜɪꜱ ɴᴜᴍʙᴇʀ.</i>", ""])

    lines.append(f"👨‍💻 <b>ᴅᴇᴠ :</b> {config.OWNER_USERNAME}")
    return "\n".join(lines)


def build_plain_export(query_num: str, records: list[dict]) -> str:
    lines = [
        "NUMBER LOOKUP RESULT",
        "====================",
        f"Searched Number : {query_num}",
        f"Total Records   : {len(records)}",
        "====================",
        "",
    ]
    for idx, rec in enumerate(records, start=1):
        lines.extend([
            f"RECORD {idx}",
            f"Name        : {rec['name']}",
            f"Parent Name : {rec['parent']}",
            f"Mobile      : {rec['number']}",
            f"Address     : {rec['address']}",
            f"Circle      : {rec['circle']}",
            f"Alternate   : {rec['alternate']}",
            f"ID Ref      : {rec['id_ref']}",
            "--------------------",
            "",
        ])
    if not records:
        lines.append("No sample records found for this query.\n")
    lines.append(f"DEV : {config.OWNER_USERNAME}")
    return "\n".join(lines)


async def num_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "⚠️ <b>ᴜꜱᴀɢᴇ:</b> <code>/num 7070230385</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    query_num = context.args[0].strip()
    records = SAMPLE_RECORDS.get(query_num, [])

    report_html = build_report(query_num, records)
    await update.message.reply_text(report_html, parse_mode=ParseMode.HTML)

    plain_text = build_plain_export(query_num, records)
    file_buf = io.BytesIO(plain_text.encode("utf-8"))
    await update.message.reply_document(
        document=InputFile(file_buf, filename=f"search_{query_num}.txt"),
        caption=f"📄 <b>ᴇxᴘᴏʀᴛ ꜰɪʟᴇ ꜰᴏʀ:</b> <code>{html.escape(query_num)}</code>",
        parse_mode=ParseMode.HTML,
    )

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    await send_log(
        context,
        "🔍 <b>#LOOKUP_QUERY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>ᴜꜱᴇʀ:</b> {format_user_tag(update)}\n"
        f"🔢 <b>ǫᴜᴇʀʏ:</b> <code>{html.escape(query_num)}</code>\n"
        f"📊 <b>ʀᴇᴄᴏʀᴅꜱ:</b> <code>{len(records)}</code>\n"
        f"🕒 <b>ᴛɪᴍᴇ:</b> <code>{now_utc}</code>",
    )


# ──────────────────── BUTTONS & CALLBACKS ──────────────────── #


async def handle_reply_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = (update.message.text or "").strip()

    if msg == "📖 ɪɴᴛʀᴏᴅᴜᴄᴛɪᴏɴ":
        await update.message.reply_text(
            "🏛️ <b>ɪɴᴛʀᴏᴅᴜᴄᴛɪᴏɴ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "• ɪɴꜱᴛᴀɴᴛ ꜰᴏʀᴍᴀᴛᴛᴇᴅ ʟᴏᴏᴋᴜᴘ ᴠɪᴇᴡ\n"
            "• ᴀᴜᴛᴏᴍᴀᴛɪᴄ <code>.txt</code> ʀᴇᴘᴏʀᴛ ᴇxᴘᴏʀᴛ\n"
            "• ᴅɪʀᴇᴄᴛ ᴜꜱᴀɢᴇ ᴡɪᴛʜᴏᴜᴛ ᴄʀᴇᴅɪᴛꜱ\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>ᴄʀᴇᴀᴛᴇᴅ ʙʏ:</b> {config.OWNER_USERNAME}",
            parse_mode=ParseMode.HTML,
            reply_markup=get_inline_links(),
        )

    elif msg == "🔢 ɴᴜᴍʙᴇʀ ɪɴꜰᴏ":
        guide = (
            "📋 <b>ʜᴏᴡ ᴛᴏ ᴜꜱᴇ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<b>ᴜꜱᴇ:</b>\n"
            "<code>/num 9106756416</code>\n\n"
            "<b>ᴇxᴀᴍᴘʟᴇ:</b>\n"
            "<code>/num 7070230385</code>\n\n"
            "<b>ꜱʏꜱᴛᴇᴍ ᴡɪʟʟ:</b>\n"
            "✅ ꜱᴄᴀɴ ᴅᴀᴛᴀʙᴀꜱᴇ\n"
            "✅ ᴀɴᴀʟʏᴢᴇ ʀᴇᴄᴏʀᴅꜱ\n"
            "✅ ɢᴇɴᴇʀᴀᴛᴇ ʀᴇᴘᴏʀᴛ\n"
            "✅ ꜱᴇɴᴅ ᴇxᴘᴏʀᴛ ꜰɪʟᴇ"
        )
        await update.message.reply_text(guide, parse_mode=ParseMode.HTML)

    elif msg == "📜 ʜᴇʟᴘ & ɢᴜɪᴅᴇ":
        await help_cmd(update, context)

    elif msg == "📞 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ":
        await update.message.reply_text(
            "📞 <b>ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>ᴏᴡɴᴇʀ:</b> {config.OWNER_USERNAME}\n"
            "💬 <b>ꜰᴏʀ ꜱᴜᴘᴘᴏʀᴛ &amp; ᴜᴘᴅᴀᴛᴇꜱ ᴜꜱᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_inline_links(),
        )

    await send_log(
        context,
        "🖱️ <b>#MENU_ACTION</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>ᴜꜱᴇʀ:</b> {format_user_tag(update)}\n"
        f"📌 <b>ʙᴜᴛᴛᴏɴ:</b> <code>{html.escape(msg)}</code>",
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "help_menu":
        text = (
            "📜 <b>ʜᴇʟᴘ &amp; ᴄᴏᴍᴍᴀɴᴅ ɢᴜɪᴅᴇ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 <code>/start</code> — ᴍᴀɪɴ ᴍᴇɴᴜ &amp; ʙᴀɴɴᴇʀ\n"
            "🔹 <code>/num &lt;number&gt;</code> — ʟᴏᴏᴋᴜᴘ + <code>.txt</code> ᴇxᴘᴏʀᴛ\n"
            "🔹 <code>/help</code> — ꜱʜᴏᴡ ʜᴇʟᴘ ᴍᴇɴᴜ\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👨‍💻 <b>ᴅᴇᴠ:</b> {config.OWNER_USERNAME}"
        )
        await query.message.reply_text(text, parse_mode=ParseMode.HTML)

    elif query.data == "usage_guide":
        text = (
            "📋 <b>ʜᴏᴡ ᴛᴏ ᴜꜱᴇ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "ꜱᴇɴᴅ: <code>/num 7070230385</code>\n\n"
            "✅ ꜱᴄᴀɴ ᴅᴀᴛᴀʙᴀꜱᴇ\n"
            "✅ ᴀɴᴀʟʏᴢᴇ ʀᴇᴄᴏʀᴅꜱ\n"
            "✅ ɢᴇɴᴇʀᴀᴛᴇ ʀᴇᴘᴏʀᴛ\n"
            "✅ ꜱᴇɴᴅ <code>.txt</code> ᴇxᴘᴏʀᴛ ꜰɪʟᴇ"
        )
        await query.message.reply_text(text, parse_mode=ParseMode.HTML)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling update:", exc_info=context.error)
    err_msg = html.escape(str(context.error))[:1500]
    await send_log(
        context,
        "⚠️ <b>#BOT_ERROR</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"<pre>{err_msg}</pre>",
    )


# ──────────────────── RENDER KEEP-ALIVE WEB SERVER ──────────────────── #


async def health_handler(request: web.Request) -> web.Response:
    return web.Response(text=f"OK - {config.BOT_USERNAME} is alive")


async def start_web_server() -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=config.PORT)
    await site.start()
    logger.info("HTTP keep-alive server listening on port %s", config.PORT)
    return runner


async def main() -> None:
    if not config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN missing in environment / config.py")

    runner = await start_web_server()

    tg_app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    tg_app.add_handler(CommandHandler("start", start_cmd))
    tg_app.add_handler(CommandHandler("help", help_cmd))
    tg_app.add_handler(CommandHandler("num", num_cmd))
    tg_app.add_handler(CallbackQueryHandler(callback_handler))
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply_buttons))
    tg_app.add_error_handler(error_handler)

    await tg_app.initialize()
    await tg_app.start()
    await tg_app.updater.start_polling(drop_pending_updates=True)

    # Startup Log
    try:
        await tg_app.bot.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=(
                "🟢 <b>#BOT_STARTED</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🤖 <b>ʙᴏᴛ:</b> {config.BOT_USERNAME}\n"
                f"👑 <b>ᴏᴡɴᴇʀ:</b> {config.OWNER_USERNAME} (<code>{config.OWNER_ID}</code>)"
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception as exc:
        logger.warning("Startup log failed: %s", exc)

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await tg_app.updater.stop()
        await tg_app.stop()
        await tg_app.shutdown()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
