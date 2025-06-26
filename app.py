import os
from telebot import TeleBot, types
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("8160988350:AAHkTPMAmQnpahK7aUZZRtnDFxQc7gVp3Lk")

bot = TeleBot(BOT_TOKEN)

# Sargyt edilen botlary saklamak üçin ýönekeý sanaw (in-memory)
bots_data = {}

# Baş menýu düwmeleri
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("➕ Bot goş"), types.KeyboardButton("ℹ️ Menýu"))
    return markup

# Bot saýlama menýusy
def bot_choice_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        types.KeyboardButton("🤝 Referal Bot"),
        types.KeyboardButton("📢 Sponsor Bot"),
        types.KeyboardButton("❌ Ýatyr")
    )
    return markup

# /start buýrugy
@bot.message_handler(commands=["start"])
def start_handler(message):
    text = f"Salam, {message.from_user.first_name}! Bu admin panel boty.\n\n" \
           "Goşmak isleýän botuňyzy saýlaň ýa-da Menýu düwmesine basyň."
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "➕ Bot goş")
def add_bot_start(message):
    bot.send_message(message.chat.id, "Haýsy bot döretmek isleýärsiňiz?", reply_markup=bot_choice_menu())

# Bot saýlamagyňyzy ýakalamak
@bot.message_handler(func=lambda m: m.text in ["🤝 Referal Bot", "📢 Sponsor Bot"])
def choose_bot(message):
    bot_name = message.text
    msg = bot.send_message(message.chat.id, f"{bot_name} üçin Token'i giriziň:")
    bot.register_next_step_handler(msg, receive_token, bot_name)

def receive_token(message, bot_name):
    token = message.text.strip()
    chat_id = message.chat.id
    # Ýönekeý token formatyny barlamak (Telegram tokeni mütlükde ':' içerýär)
    if ':' not in token:
        msg = bot.send_message(chat_id, "Nädogry token formaty! Täzeden synanyşyň:")
        bot.register_next_step_handler(msg, receive_token, bot_name)
        return

    # Botlary saklamak (bu diňe ýatlama, köprü bazasy däl)
    bots_data[chat_id] = {"bot_name": bot_name, "token": token}

    text = f"{bot_name} üstünlikli goşuldy!\n" \
           f"Botuň tokeni saklandy. Indi admin panelini ulanyp bilersiňiz.\n\n" \
           f"Goşmaça işlemler üçin düwmeleri ulanyň."

    # Ýönekeý admin panel menýusy
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📊 Statistika"),
        types.KeyboardButton("⚙️ Menýu ýazgyny üýtget"),
        types.KeyboardButton("🛑 Bot öçür"),
        types.KeyboardButton("🏠 Baş menýu"),
    )
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🏠 Baş menýu")
def go_main_menu(message):
    bot.send_message(message.chat.id, "Baş menýu:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🛑 Bot öçür")
def remove_bot(message):
    chat_id = message.chat.id
    if chat_id in bots_data:
        del bots_data[chat_id]
        bot.send_message(chat_id, "Bot üstünlikli öçürildi!")
    else:
        bot.send_message(chat_id, "Öçürmek üçin goşulan bot tapylmady.")

@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def show_stats(message):
    chat_id = message.chat.id
    if chat_id in bots_data:
        bot_info = bots_data[chat_id]
        bot.send_message(chat_id, f"Goşulan bot: {bot_info['bot_name']}\nToken: {bot_info['token']}")
    else:
        bot.send_message(chat_id, "Goşulan bot tapylmady.")

@bot.message_handler(func=lambda m: m.text == "⚙️ Menýu ýazgyny üýtget")
def edit_menu(message):
    bot.send_message(message.chat.id, "Bu funksiýa häzirlikçe işlenýär...")

@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, "Häzirlikçe diňe menýudaky düwmeler işlenýär.")

if __name__ == "__main__":
    print("Bot işleýär...")
    bot.infinity_polling()
