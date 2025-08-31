import telebot
from telebot import types
import schedule
import time
import datetime

TOKEN = "ТВОЙ_ТОКЕН"
bot = telebot.TeleBot(TOKEN)

# Здесь будем хранить состояние пользователей
# Формат: {chat_id: {"task": int, "waiting": bool}}
# task = 0 (ещё не начали), 1, 2, 3...
# waiting = True -> ждём ответа "да/нет"
user_state = {}

# --- Команда /start ---
@bot.message_handler(commands=["start"])
def start_message(message):
    chat_id = message.chat.id
    user_state[chat_id] = {"task": 0, "waiting": False}
    bot.send_message(chat_id, "Привет! Я буду присылать тебе задания каждое утро в 9:00.")

# --- Функция для отправки задания или вопроса ---
def morning_job():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{now}] Проверка расписания...")

    for chat_id, state in user_state.items():
        task = state["task"]
        waiting = state["waiting"]

        if task == 0:  
            # Первый день — отправляем Задание 1
            bot.send_message(chat_id, "Задание 1")
            state["task"] = 1
            state["waiting"] = True

        elif waiting:  
            # Ждём ответа по текущему заданию
            markup = types.InlineKeyboardMarkup()
            btn_yes = types.InlineKeyboardButton("Да", callback_data="yes")
            btn_no = types.InlineKeyboardButton("Нет", callback_data="no")
            markup.add(btn_yes, btn_no)
            bot.send_message(chat_id, "Вы справились с заданием?", reply_markup=markup)

        else:  
            # Если ждать не надо — просто продолжаем (например, если уже закончили)
            pass

# --- Обработка нажатий на кнопки ---
@bot.callback_query_handler(func=lambda call: True)
def handle_answer(call):
    chat_id = call.message.chat.id
    state = user_state.get(chat_id, {"task": 0, "waiting": False})

    if call.data == "yes":
        if state["task"] == 1:
            bot.send_message(chat_id, "Задание 2")
            state["task"] = 2
            state["waiting"] = True

        elif state["task"] == 2:
            bot.send_message(chat_id, "Задание 3")
            state["task"] = 3
            state["waiting"] = True

        elif state["task"] == 3:
            bot.send_message(chat_id, "Спасибо за участие!")
            state["waiting"] = False  # конец игры

    elif call.data == "no":
        bot.send_message(chat_id, "Очень жаль 😿. Попробуем ещё раз завтра!")
        state["waiting"] = True  # завтра снова спросим

    user_state[chat_id] = state
    bot.answer_callback_query(call.id)

# --- Планировщик: каждый день в 9:00 ---
schedule.every().day.at("09:00").do(morning_job)

print("Бот запущен. Ждём 9 утра...")

# --- Основной цикл ---
while True:
    schedule.run_pending()
    bot.polling(none_stop=True, interval=0, timeout=20)
    time.sleep(1)
