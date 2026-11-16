import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
UPI_ID = os.environ.get("UPI_ID", "yourupi@okhdfc")

tournaments = {
    "ffi_daily": {"name": "FFI DAILY - Full Map | 12 PM", "fee": 30, "prize": 500, "slots": 48, "joined": []},
    "ffi_evening": {"name": "FFI EVENING - Bermuda | 7 PM", "fee": 50, "prize": 1000, "slots": 48, "joined": []}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏆 Tournaments Dekho", callback_data="list")],
        [InlineKeyboardButton("💰 My Wallet", callback_data="wallet")],
        [InlineKeyboardButton("📞 Support", callback_data="support")]
    ]
    await update.message.reply_text("🔥 *FFI TOURNAMENT BOT me Welcome!*\n\nRoz jeeto, roz kamao.\nNeeche se Tournament chuno.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "list":
        kb = []
        for key, t in tournaments.items():
            left = t["slots"] - len(t["joined"])
            kb.append([InlineKeyboardButton(f"{t['name']} | ₹{t['fee']} | {left} Left", callback_data=f"join_{key}")])
        kb.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
        await q.edit_message_text("🏆 *Available Tournaments:*", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    elif q.data.startswith("join_"):
        key = q.data.split("_")[1] + "_" + q.data.split("_")[2] if len(q.data.split("_"))>2 else q.data.replace("join_","")
        # simple fix
        key = q.data.replace("join_","")
        t = tournaments.get(key)
        if not t:
            await q.edit_message_text("Tournament nahi mila.")
            return
        context.user_data["joining"] = key
        await q.edit_message_text(f"🏆 *{t['name']}*\n\nEntry Fee: ₹{t['fee']}\nPrize: ₹{t['prize']}\n\nPayment ke liye is UPI par ₹{t['fee']} bhejo:\n`{UPI_ID}`\n\nBhejne ke baad UTR / Screenshot yahan bhejo.", parse_mode="Markdown")
    elif q.data == "back":
        await q.edit_message_text("🔥 FFI TOURNAMENT BOT\n/start dabao dobara shuru karne ke liye.")
    elif q.data == "wallet":
        await q.edit_message_text("💰 Wallet: ₹0\nJeetne ke baad yahan prize aayega.")
    elif q.data == "support":
        await q.edit_message_text("📞 Support ke liye Admin ko message karo.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get("joining")
    if not key:
        await update.message.reply_text("Pehle /start karke tournament join karo.")
        return
    t = tournaments[key]
    user = update.effective_user
    await update.message.reply_text(f"✅ Screenshot mil gaya {user.first_name}!\n\nTournament: {t['name']}\nAdmin check karke tumhe approve karega. Room ID match se 10 min pehle milegi.")
    if ADMIN_ID:
        try:
            await context.bot.send_message(ADMIN_ID, f"🔔 Naya Payment!\nUser: {user.first_name} (@{user.username}) ID: {user.id}\nTournament: {t['name']}\nFee: ₹{t['fee']}")
        except: pass

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("joining"):
        await handle_photo(update, context)
    else:
        await update.message.reply_text("Tournament join karne ke liye /start dabao.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
