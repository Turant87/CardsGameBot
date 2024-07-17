from random import choice
import telebot

TOKEN = '7270173719:AAGXybibgIJ2O2ZmEMJnuDoNosierURTpIE'
bot = telebot.TeleBot(TOKEN)

users_data = {}


@bot.message_handler(commands=['start'])
def start(message):
    keybord = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = telebot.types.KeyboardButton('Начать игру')
    keybord.add(start_button)
    bot.send_message(message.chat.id, 'Добро пожаловать в игру! Нажмите "Начать игру" для начала.',
                     reply_markup=keybord)


@bot.message_handler(func=lambda message: message.text == 'Начать игру')
def choose_difficulty(message):
    keybord = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keybord.row('1 - Угадать только цвет масти')
    keybord.row('2 - Угадать значение карты и цвет масти')
    keybord.row('3 - Угадать значение карты и масть')
    bot.send_message(message.chat.id, 'Выберите уровень сложности:', reply_markup=keybord)
    bot.register_next_step_handler(message, set_difficulty)


def set_difficulty(message):
    difficulty = message.text.split(' ')[0]
    if difficulty in ['1', '2', '3']:
        users_data[message.chat.id] = {'difficulty': difficulty, 'score': 0, 'round': 0}
        bot.send_message(message.chat.id, 'Введите количество раундов (1-100):')
        bot.register_next_step_handler(message, set_rounds)
    else:
        bot.send_message(message.chat.id, 'Некорректный ввод. Попробуйте снова.')
        choose_difficulty(message)


def set_rounds(message):
    try:
        num_rounds = int(message.text)
        if 1 <= num_rounds <= 100:
            users_data[message.chat.id]['num_rounds'] = num_rounds
            play_round(message)
        else:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, 'Некорректный ввод. Введите количество раундов (1-100):')
        bot.register_next_step_handler(message, set_rounds)


def get_card():
    CARD_NUMBER = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'в', 'д', 'к', 'т']
    CARD_SUIT = ['бубны', 'черви', 'пики', 'трефы']
    random_card_number = choice(CARD_NUMBER)
    random_card_suit = choice(CARD_SUIT)
    return random_card_number, random_card_suit


def play_round(message):
    user_data = users_data[message.chat.id]
    user_data['round'] += 1
    card_number, card_suit = get_card()
    user_data['current_card'] = (card_number, card_suit)

    if user_data['difficulty'] == '1':
        keybord = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keybord.row('🟥 Красный', '⬛ Черный')
        bot.send_message(message.chat.id, 'Введите цвет масти карты (Черный или Красный):', reply_markup=keybord)
    elif user_data['difficulty'] == '2':
        bot.send_message(message.chat.id, 'Введите цвет масти карты (Черный или Красный):')
    elif user_data['difficulty'] == '3':
        bot.send_message(message.chat.id, 'Введите значение карты (2, 3, 4, 5, 6, 7, 8, 9, 10, в, д, к, т):')

    bot.register_next_step_handler(message, compare_answer)


def compare_answer(message):
    user_data = users_data[message.chat.id]
    card_number, card_suit = user_data['current_card']
    difficulty = user_data['difficulty']

    if difficulty == '1':
        if (message.text in ['🟥', 'красный'] and card_suit in ['бубны', 'черви']) or \
                (message.text in ['⬛', 'черный'] and card_suit in ['пики', 'трефы']):
            user_data['score'] += 1
            bot.send_message(message.chat.id, f'Вы угадали! Карта была - {card_number} {card_suit}')
        else:
            bot.send_message(message.chat.id, f'Вы не угадали, карта была - {card_number} {card_suit}')

    elif difficulty == '2':
        bot.send_message(message.chat.id, 'Введите значение карты (2, 3, 4, 5, 6, 7, 8, 9, 10, в, д, к, т):')
        bot.register_next_step_handler(message, compare_number)

    elif difficulty == '3':
        player_number = message.text.strip().lower()
        if player_number == card_number:
            bot.send_message(message.chat.id, 'Введите масть карты (бубны, черви, пики, трефы):')
            bot.register_next_step_handler(message, compare_suit)
        else:
            bot.send_message(message.chat.id, f'Вы не угадали значение карты. Карта была - {card_number} {card_suit}')
            next_round(message)


def compare_number(message):
    user_data = users_data[message.chat.id]
    card_number, card_suit = user_data['current_card']
    player_number = message.text.strip().lower()

    if player_number == card_number:
        if user_data['difficulty'] == '2':
            bot.send_message(message.chat.id, 'Введите цвет масти карты (Черный или Красный):')
            bot.register_next_step_handler(message, compare_color)
        elif user_data['difficulty'] == '3':
            bot.send_message(message.chat.id, 'Введите масть карты (бубны, черви, пики, трефы):')
            bot.register_next_step_handler(message, compare_suit)
    else:
        bot.send_message(message.chat.id, f'Вы не угадали значение карты. Карта была - {card_number} {card_suit}')
        next_round(message)


def compare_color(message):
    user_data = users_data[message.chat.id]
    card_number, card_suit = user_data['current_card']
    player_suit_color = message.text.strip().lower()

    if (player_suit_color == 'красный' and card_suit in ['бубны', 'черви']) or \
            (player_suit_color == 'черный' and card_suit in ['пики', 'трефы']):
        user_data['score'] += 2
        bot.send_message(message.chat.id, f'Вы угадали! Карта была - {card_number} {card_suit}')
    else:
        bot.send_message(message.chat.id, f'Вы не угадали цвет масти карты. Карта была - {card_number} {card_suit}')

    next_round(message)


def compare_suit(message):
    user_data = users_data[message.chat.id]
    card_number, card_suit = user_data['current_card']
    player_suit = message.text.strip().lower()

    if player_suit == card_suit:
        user_data['score'] += 3
        bot.send_message(message.chat.id, f'Вы угадали! Карта была - {card_number} {card_suit}')
    else:
        bot.send_message(message.chat.id, f'Вы не угадали масть карты. Карта была - {card_number} {card_suit}')

    next_round(message)


def next_round(message):
    user_data = users_data[message.chat.id]
    if user_data['round'] < user_data['num_rounds']:
        play_round(message)
    else:
        bot.send_message(message.chat.id, f'Игра окончена. Ваш счёт: {user_data["score"]}')
        start(message)


bot.infinity_polling()


