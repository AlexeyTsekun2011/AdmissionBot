from config import TOKEN
import json
import telebot
from telebot import types
from datetime import date, timedelta

bot = telebot.TeleBot(TOKEN)
try:
    with open("data.json", "r", encoding="utf-8") as file:
        user_data = json.load(file)
except FileNotFoundError:
    user_data = {}


@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    bot.send_message(message.chat.id, "Добро пожаловать в бот регистрации на стрижку онлайн!\n"
                                      "/register - регистрация\n"
                                      "/appoint - запись на услугу\n"
                                      "/add_review - оставить отзыв")


@bot.message_handler(commands=["appoint"])
def handle_show_dates(message: types.Message):
    keyboard_data = generate_keyboard_data()
    bot.send_message(message.chat.id, "Выберите день", reply_markup=keyboard_data)


@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    if call.data.startswith("data"):
        _, data = call.data.split("_")
        keyboard_hours = generate_keyboard_hours(chosen_date=data)
        bot.send_message(call.message.chat.id, "Выберите время", reply_markup=keyboard_hours)
    if call.data.startswith("hours"):
        _, hours, day = call.data.split("_")
        bot.send_message(call.message.chat.id, f"Вы выбрали дату {day} {hours}")
        add_appointment(day, hours, call.message.chat.id)


@bot.message_handler(commands=["register"])
def handle_set_name(message: types.Message):
    bot.send_message(message.chat.id, "Введите своё имя")
    bot.register_next_step_handler_by_chat_id(message.chat.id, handle_addname)

@bot.message_handler(commands=["add_review"])
def handle_add_review(message:types.Message):
    bot.send_message(message.chat.id,"Отправьте свой отзыв")
    bot.register_next_step_handler_by_chat_id(message.chat.id,save_review)



def save_review(message:types.Message):
    user_review = message.text
    if len(user_review) != 0:
        chat_id = message.chat.id
        add_review(chat_id,user_review)
        bot.send_message(chat_id,"Благодарим за отзыв")

def handle_addname(message: types.Message):
    global user_data
    user_name = message.text
    if len(user_name) != 0:
        chat_id = message.chat.id
        user_data["clients"][str(chat_id)] = user_name
        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(user_data, file, ensure_ascii=False, indent=4)
        bot.send_message(chat_id, "Имя добавлено")
    else:
        bot.send_message(message.chat.id, "Ошибка ввода")


def generate_keyboard_data():
    keyboard = types.InlineKeyboardMarkup()
    dates = [date.today() + timedelta(days=3 + i) for i in range(0, 7)]
    # for i in range(0, 7):
    #     dates.append(datetime.today() + timedelta(days=3 + i))
    for i in dates:
        button = types.InlineKeyboardButton(text=f"{i}", callback_data=f"data_{i}")
        keyboard.add(button)
    return keyboard


def generate_keyboard_hours(chosen_date):
    keyboard = types.InlineKeyboardMarkup()
    hours = ["10:00", "12:00", "15:00", "17:00"]
    for appointment in user_data["appointments"]:
        if chosen_date == appointment["date"]:
            hours.remove(appointment["time"])

    for i in hours:
        button = types.InlineKeyboardButton(text=f"{i}", callback_data=f"hours_{i}_{chosen_date}")
        keyboard.add(button)
    return keyboard


def add_appointment(date, time, client):
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            saved_info = json.load(file)
    except FileNotFoundError:
        saved_info = {"appointments": [], "reviews": []}

    saved_info["appointments"].append({"date": date, "time": time, "client": client})
    with open("data.json", "w", encoding="utf-8") as write_file:
        json.dump(saved_info, write_file, ensure_ascii=False, indent=4)


def add_review(client, text):
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            saved_info = json.load(file)
    except FileNotFoundError:
        saved_info = {"appointments": [], "reviews": []}

    saved_info["reviews"].append({"client": client, "text": text})
    with open("data.json", "w", encoding="utf-8") as write_file:
        json.dump(saved_info, write_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    bot.polling(none_stop=True)
