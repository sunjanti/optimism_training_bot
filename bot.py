import telebot
from telebot import types
import schedule
import time
import datetime
import threading

TOKEN = "8334888358:AAG4XN5T-sYker_C0Dar8_ujRyMbNduqIOA"
bot = telebot.TeleBot(TOKEN)

# ===== Тексты =====
WELCOME_TEXT = """
<b>Бот-курс повышения оптимизма</b>  

Зачем нужен оптимизм?
Ученые разных стран изучают, что же делает человека счастливее, улучшает качество жизни и здоровья.
Различные научные направления выделяют такие факторы, как: 
-понимание своих желаний
-жизнь в соответствии со своими ценностями
-наличие жизненного смысла
-позитивное отношение к себе, другим, к жизни  
На последнем мы и остановимся с вами, а именно, на оптимизме.

По многим исследованиям, оптимизм значительно меняет жизнь к лучшему.
Оптимизм - это позитивный взгляд на жизнь, вера в благоприятный исход событий и в собственные силы, а также жизнерадостное мироощущение. Простыми словами, это привычка находить хорошее, чему можно радоваться. Эту привычку можно и полезно развивать.
Именно этим мы и займемся.

Как известно, эмоции подпитываются мыслями.
Здесь, с нами, Вы будете тренироваться радоваться!
Да, да, именно тренироваться, ведь радоваться или грустить - это в определенной степени ПРИВЫЧКА быть оптимистом.
Оптимисты находят в реальности поводы для радости, в то время как пессимисты в реальности привыкли замечать грустные моменты.
А именно радость и оптимизм улучшает настроение и жизнь в целом.

О курсе.
Бот курс повышения оптимизма длится три дня.
Утром вам будет приходить задание, которое нужно будет выполнить за день.
В конце дня оценить свое выполнение, чтобы получить следующее задание утром.

Готовы к бот курсу повышения оптимизма?
"""

TASK_1 = "Задание 1"
TASK_2 = "Задание 2"
TASK_3 = "Задание 3"
QUESTION = "Вы справились с заданием?"
SORRY_TEXT = "Очень жаль 😿. Попробуем ещё раз завтра!"
THANKS_TEXT = "Спасибо за участие! 🎉"

# Здесь будем хранить состояние пользователей
# Формат: {chat_id: {"task": int, "active": bool}}
# task = 0 (ещё не начали), 1, 2, 3...
user_state = {}

# --- Команда /start ---
@bot.message_handler(commands=["start"])
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "начать")
def start_message(message):
    chat_id = message.chat.id
    user_state[chat_id] = {"task": 0, "active": False}

    markup = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("Да", callback_data="ready_yes")
    btn_no = types.InlineKeyboardButton("Нет", callback_data="ready_no")
    markup.add(btn_yes, btn_no)

    bot.send_message(chat_id, WELCOME_TEXT, parse_mode="HTML", reply_markup=markup)

#  Ответы на кнопки "Да" / "Нет"
@bot.callback_query_handler(func=lambda call: call.data in ["ready_yes", "ready_no"])
def callback_ready(call):
    chat_id = call.message.chat.id

    if call.data == "ready_yes":
        bot.send_message(chat_id,
                         "Поздравляем! Мы рады вашему участию! "
                         "Завтра утром вам придет задание. Хорошего вам дня!")
        user_state[chat_id]["active"] = True
        user_state[chat_id]["task"] = 0  # пока нет заданий, начнём завтра

    elif call.data == "ready_no":
        bot.send_message(chat_id,
                         "Спасибо за участие, обязательно возвращайтесь снова.\n"
                         "Когда захотите начать курс, напишите 'Начать'. Удачи вам! ✨")
        user_state[chat_id]["active"] = False
        user_state[chat_id]["task"] = 0

# --- Функция для отправки задания или вопроса ---
def morning_job():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{now}] Проверка расписания...")

    for chat_id, state in user_state.items():
        task = state["task"]
        active = state["active"]

        if not active:
            continue  # если пользователь не активен — пропускаем

        if task == 0:  
            # Первый день — отправляем Задание 1
            bot.send_message(chat_id, TASK_1)
            state["task"] = 1

        elif task in [1, 2, 3]:
            # Спрашиваем, справились ли с заданием
            markup = types.InlineKeyboardMarkup()
            btn_yes = types.InlineKeyboardButton("Да", callback_data="yes")
            btn_no = types.InlineKeyboardButton("Нет", callback_data="no")
            markup.add(btn_yes, btn_no)
            bot.send_message(chat_id, QUESTION, reply_markup=markup)

# --- Обработка нажатий на кнопки ---
@bot.callback_query_handler(func=lambda call: call.data in ["yes", "no"])
def handle_answer(call):
    chat_id = call.message.chat.id
    state = user_state.get(chat_id, {"task": 0, "active": False})

    if not state["active"]:
        return

    if call.data == "yes":
        if state["task"] == 1:
            bot.send_message(chat_id, TASK_2)
            state["task"] = 2

        elif state["task"] == 2:
            bot.send_message(chat_id, TASK_3)
            state["task"] = 3

        elif state["task"] == 3:
            bot.send_message(chat_id, THANKS_TEXT)
            state["active"] = False  # курс завершён

    elif call.data == "no":
        bot.send_message(chat_id, SORRY_TEXT)
        # остаёмся на том же задании, курс продолжается

    user_state[chat_id] = state
    bot.answer_callback_query(call.id)

# --- Планировщик: каждый день в 9:00 ---
schedule.every().day.at("04:00").do(morning_job)

print("Бот запущен. Ждём 9 утра...")

# --- Основной цикл ---
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# запускаем планировщик параллельно с polling
threading.Thread(target=run_schedule, daemon=True).start()

# основной процесс — слушает команды
bot.polling(none_stop=True, interval=0, timeout=20)


