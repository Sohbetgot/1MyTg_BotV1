import telebot
from telebot import types

TOKEN = "8160988350:AAHkTPMAmQnpahK7aUZZRtnDFxQc7gVp3Lk"
bot = telebot.TeleBot(TOKEN)

bot_types = {
    "1": "Referal Bot",
    "2": "Sponsor Bot"
}

# Ulanyjynyň botlary: {user_id: [{"bot_type": ..., "bot_token": ..., "bot_username": ...}, ...]}
user_bots = {}

# Ulanyjynyň haýsy ädimde işleýändigini saklaýar
user_states = {}

def get_bot_username(token):
    # Bot token bilen bot adyny almak üçin isleg
    # Bu funksiýa haçan-da, soň token alnan soň, botyň @username-ni tapmak üçin ulanylýar
    import requests
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            result = r.json()
            if result.get("ok"):
                return result["result"]["username"]
    except:
        pass
    return None

@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Bot goş", "Meniň botlar")
    bot.send_message(message.chat.id, "Salam! Näme etmek isleýärsiňiz?", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "Bot goş")
def bot_add_choose_type(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, resize_keyboard=True)
    for key, name in bot_types.items():
        markup.add(f"{key}. {name}")
    bot.send_message(message.chat.id, "Haýsy boty goşmak isleýärsiňiz? Sanawy saýlaň:", reply_markup=markup)
    user_states[message.from_user.id] = {"step": "choose_bot_type"}

@bot.message_handler(func=lambda m: m.text == "Meniň botlar")
def my_bots_list(message):
    user_id = message.from_user.id
    bots = user_bots.get(user_id)
    if not bots:
        bot.send_message(message.chat.id, "Siziň goşan botlaryňyz ýok.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i, b in enumerate(bots, 1):
        markup.add(f"{i}. @{b['bot_username']} ({bot_types.get(b['bot_type'], 'Namdan bot')})")
    markup.add("Yza")
    bot.send_message(message.chat.id, "Siziň botlaryňyz:", reply_markup=markup)
    user_states[user_id] = {"step": "choose_my_bot", "bots": bots}

@bot.message_handler(func=lambda m: m.from_user.id in user_states)
def handle_steps(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    if not state:
        return

    if state.get("step") == "choose_bot_type":
        choice = message.text.split(".")[0]
        if choice in bot_types:
            user_states[user_id]["bot_type"] = choice
            user_states[user_id]["step"] = "get_token"
            bot.send_message(message.chat.id, f"{bot_types[choice]} üçin Bot Token-iňi iberiň:")
        else:
            bot.send_message(message.chat.id, "Nädogry saýlaw, haýyşyňyz täzeden saýlaň.")

    elif state.get("step") == "get_token":
        token = message.text.strip()
        if ":" not in token:
            bot.send_message(message.chat.id, "Nädogry token. Täzeden synanyşyň.")
            return
        username = get_bot_username(token)
        if not username:
            bot.send_message(message.chat.id, "Token dogry däl ýa-da baglanyşykda problem bar.")
            return
        # Bot ulanyjynyň sanawyna goş
        bots = user_bots.get(user_id, [])
        bots.append({
            "bot_type": user_states[user_id]["bot_type"],
            "bot_token": token,
            "bot_username": username
        })
        user_bots[user_id] = bots
        user_states.pop(user_id)
        bot.send_message(message.chat.id, f"Bot üstünlikli goşuldy: @{username}")
    elif state.get("step") == "choose_my_bot":
        if message.text == "Yza":
            user_states.pop(user_id)
            start(message)
            return
        # Ulanyjy saýlan bot nomerini berýän bolsa
        try:
            index = int(message.text.split(".")[0]) - 1
            bots = state.get("bots", [])
            if index < 0 or index >= len(bots):
                raise ValueError
            selected_bot = bots[index]
            # Bu ýerde admin paneli açyp bolar
            bot.send_message(message.chat.id, f"Şu bot saýlandy: @{selected_bot['bot_username']}\nAdmin panel häzir ýok, ýöne goşmak bolýar.")
            user_states.pop(user_id)
        except:
            bot.send_message(message.chat.id, "Nädogry saýlaw. Täzeden synanyşyň.")
    else:
        bot.send_message(message.chat.id, "Haýyşyňyzy düşünmedim. Täzeden /start ýazyň.")

bot.infinity_polling()
