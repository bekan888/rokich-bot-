import telebot
from telebot import types
import os
from datetime import datetime

# ЗАМЕНИ НА СВОЙ ТОКЕН
TOKEN = '9094816290:AAG4XodU-zfkYELvR-_lWd6DWAwMV4wprcs'
bot = telebot.TeleBot(TOKEN)

# --- Данные из документа ---
TERMINAL_VALUES = [
    "Faol va mazmunli hayot", "Hayotiy donolik", "Sog'liq", "Qiziqarli ish",
    "Tabiat va san'at go'zalligi", "Sevgi", "Moddiy jihatdan ta'minlangan hayot",
    "Yaxshi va sodiq do'stlarga ega bo'lish", "Jamiyat tomonidan tan olinish",
    "Bilim olish va dunyoni anglash", "Samarali va unumli hayot", "Shaxsiy rivojlanish",
    "Ko'ngilochar hayot", "Erkinlik va mustaqillik", "Baxtli oilaviy hayot",
    "Boshqalarning baxt-saodati", "Ijodkorlik", "O'ziga ishonch va ichki xotirjamlik"
]

INSTRUMENTAL_VALUES = [
    "Ozodalik va tartiblilik", "Odoblilik va tarbiyalilik", "Yuqori talabchanlik",
    "Quvnoqlik va hayotsevarlik", "Ijrochilik va intizomlilik", "Mustaqillik",
    "O'zidagi va boshqalardagi kamchiliklarga murosasiz munosabat",
    "Bilimdonlik va ma'rifatlilik", "Mas'uliyatlilik", "Oqilonalik va mantiqiy fikrlash",
    "O'zini nazorat qilish", "O'z fikrini himoya qilishda jasorat", "Qat'iy iroda",
    "Bag'rikenglik", "Keng dunyoqarash", "Halollik", "Ishda samaradorlik",
    "Boshqalarga nisbatan sezgirlik va e'tiborlilik"
]

# Хранилище данных пользователей
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {
        'step': 'ask_fio',
        'fio': '', 'sinf': '', 'sana': '', 'maktab': '',
        'terminal': {}, 'instrumental': {},
        'current_list': 'terminal', 'current_index': 0
    }
    bot.send_message(chat_id, "Assalomu alaykum! Bu M. Rokichning \"Qadriyatlar metodikasi\" bo'yicha so'rovnoma.\n\nIltimos, o'quvchining **F.I.Sh.** (Familiya, Ism, Sharif) ni kiriting:", parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "Iltimos, /start buyrug'ini bosing.")
        return

    data = user_data[chat_id]
    text = message.text.strip()

    # Шаг 1: ФИО
    if data['step'] == 'ask_fio':
        data['fio'] = text
        data['step'] = 'ask_sinf'
        bot.send_message(chat_id, "Sinfni kiriting (masalan: 9-A):")
    
    # Шаг 2: Класс
    elif data['step'] == 'ask_sinf':
        data['sinf'] = text
        data['step'] = 'ask_sana'
        bot.send_message(chat_id, "Sanani kiriting (masalan: 24.05.2024):")
        
    # Шаг 3: Дата
    elif data['step'] == 'ask_sana':
        data['sana'] = text
        data['step'] = 'ask_maktab'
        bot.send_message(chat_id, "Maktab nomini kiriting:")
        
    # Шаг 4: Школа и переход к тесту
    elif data['step'] == 'ask_maktab':
        data['maktab'] = text
        data['step'] = 'testing'
        bot.send_message(chat_id, f"Rahmat, {data['fio']}!\n\nEndi test boshlanadi. Sizga 18 ta terminal qadriyat beriladi. Har biriga 1 dan 18 gacha o'rin bering (1 - eng muhim, 18 - eng kam muhim).\n\nHar bir raqam faqat bir marta ishlatilishi kerak.")
        send_next_value(chat_id)
        
    # Шаг 5: Ответы на тест (цифры)
    elif data['step'] == 'testing':
        try:
            rank = int(text)
            if not (1 <= rank <= 18):
                raise ValueError
            
            current_dict = data['terminal'] if data['current_list'] == 'terminal' else data['instrumental']
            if rank in current_dict.values():
                bot.send_message(chat_id, "Bu raqam allaqachon ishlatilgan! Boshqa raqam kiriting.")
                return
            
            current_values = TERMINAL_VALUES if data['current_list'] == 'terminal' else INSTRUMENTAL_VALUES
            current_dict[current_values[data['current_index']]] = rank
            
            data['current_index'] += 1
            send_next_value(chat_id)

        except ValueError:
            bot.send_message(chat_id, "Iltimos, faqat 1 dan 18 gacha bo'lgan butun son kiriting.")

def send_next_value(chat_id):
    data = user_data[chat_id]
    values = TERMINAL_VALUES if data['current_list'] == 'terminal' else INSTRUMENTAL_VALUES
    idx = data['current_index']
    
    if idx < len(values):
        # Считаем использованные ранги
        current_dict = data['terminal'] if data['current_list'] == 'terminal' else data['instrumental']
        used_ranks = list(current_dict.values())
        free_ranks = [i for i in range(1, 19) if i not in used_ranks]
        
        list_name = "Terminal" if data['current_list'] == 'terminal' else "Instrumental"
        text = f"**{list_name} ro'yxati ({idx + 1}/18)**\n\n"
        text += f"**{values[idx]}**\n\n"
        text += f"Bu qadriyat uchun o'rin kiriting.\nBo'sh raqamlar: {', '.join(map(str, free_ranks))}"
        
        bot.send_message(chat_id, text, parse_mode='Markdown')
    else:
        if data['current_list'] == 'terminal':
            data['current_list'] = 'instrumental'
            data['current_index'] = 0
            bot.send_message(chat_id, "✅ Birinchi ro'yxat tugadi! Endi ikkinchi ro'yxat - **Instrumental qadriyatlar** boshlanadi.", parse_mode='Markdown')
            send_next_value(chat_id)
        else:
            show_results(chat_id)

def show_results(chat_id):
    data = user_data[chat_id]
    
    # Сортируем
    sorted_terminal = sorted(data['terminal'].items(), key=lambda item: item[1])
    sorted_instr = sorted(data['instrumental'].items(), key=lambda item: item[1])
    
    # Формируем итоговое сообщение (как в документе)
    text = f"📋 **NATIJALAR:**\n"
    text += f"**O'quvchi:** {data['fio']}\n"
    text += f"**Sinf:** {data['sinf']} | **Sana:** {data['sana']}\n"
    text += f"**Maktab:** {data['maktab']}\n\n"
    
    text += "📌 **TERMINAL QADRIYATLAR (1-18):**\n"
    for rank, (val, _) in enumerate(sorted_terminal, 1):
        text += f"{rank}. {val}\n"
        
    text += "\n📌 **INSTRUMENTAL QADRIYATLAR (1-18):**\n"
    for rank, (val, _) in enumerate(sorted_instr, 1):
        text += f"{rank}. {val}\n"

    text += "\n📊 **NATIJALARNI QAYD ETISH JADVALI:**\n"
    text += "```\n"
    text += "Ko'rsatkich      | 1-5 | 6-10 | 11-18\n"
    text += "Terminal        |  " + str(len([r for r in data['terminal'].values() if 1 <= r <= 5])) + "   |   " + str(len([r for r in data['terminal'].values() if 6 <= r <= 10])) + "   |   " + str(len([r for r in data['terminal'].values() if 11 <= r <= 18])) + "\n"
    text += "Instrumental    |  " + str(len([r for r in data['instrumental'].values() if 1 <= r <= 5])) + "   |   " + str(len([r for r in data['instrumental'].values() if 6 <= r <= 10])) + "   |   " + str(len([r for r in data['instrumental'].values() if 11 <= r <= 18])) + "\n"
    text += "```\n\n"

    # Вывод (Xulosa) - Топ 5
    text += "📝 **MAKTAB MASLAHATCHISI XULOSASI:**\n"
    text += "Aniqlangan yetakchi qadriyatlar (Top 5):\n"
    for i in range(5):
        text += f"{i+1}. {sorted_terminal[i][0]}\n"
        
    text += "\nTarbiyaviy tavsiyalar:\n"
    text += "O'quvchining ustuvor qadriyatlariga e'tibor qaratish va shu yo'nalishda rivojlantirish tavsiya etiladi."
    
    # Отправляем частями, если текст слишком длинный
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            bot.send_message(chat_id, text[i:i+4000], parse_mode='Markdown')
    else:
        bot.send_message(chat_id, text, parse_mode='Markdown')
        
    bot.send_message(chat_id, "Yangi o'quvchi uchun /start bosing.")
    del user_data[chat_id]

if __name__ == '__main__':
    print("Bot ishga tushdi...")
    bot.infinity_polling()
