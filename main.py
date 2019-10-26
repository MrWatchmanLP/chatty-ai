import os.path
import random
import emoji
import datetime
import mc

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from string import punctuation

token = "8ebd06e6b39901e266522e3bfb750bec56002534ff8d0f9faa8acc1b2a28422770ed7eca2e0dbe30e4ea5"
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 178923582)

messages_counter = 0
messages_limit = 50
commands = """Команды бота:\n01)@chattyai команды - выводит этот список\n02)@chattyai рыгни - рыгает\n03)@chattyai 
анекдот - рассказывает анекдот\n04)@chattyai когда заговоришь - сообщает через сколько сообщений бот 
заговорит\n05)@chattyai лимит (10-99)- устанавливает лимит сообщений сампроизвольного сообщения от бота\n06)@chattyai 
очистить - очищает данные для обучения """


def create_keyboard(response):
    keyboard = VkKeyboard(one_time=False)

    if response == 'тест':
        keyboard.add_button('Белая кнопка', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Зелёная кнопка', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Синяя кнопка', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Красная кнопка', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Привет', color=VkKeyboardColor.PRIMARY)
    elif response == 'закрыть':
        return keyboard.get_empty_keyboard()

    keyboard = keyboard.get_keyboard()
    return keyboard


def send_message(session_api, peer_id, message=None, attachment=None, keyboard=None, payload=None):
    session_api.messages.send(peer_id=peer_id, message=message, random_id=random.randint(-2147483648, +2147483648),
                              attachment=attachment, keyboard=keyboard, payload=payload)


def set_limit(limit):
    global messages_limit
    if limit >= 10:
        messages_limit = limit


def create_or_clear_file(name_of_file):
    file = open(name_of_file, "w")
    file.close()
    print("Created file with name " + name_of_file + " at " + str(datetime.datetime.now()))


def append_file(name_of_file, line):
    name = str(name_of_file) + '.txt'
    with open(name, 'a') as file:
        file.write(line + '\n')


def check_peer_id(chat_id):
    name = str(chat_id) + '.txt'
    if not os.path.exists(name):
        create_or_clear_file(name)


def extract_emojis(line):
    return ''.join(c for c in line if c not in emoji.UNICODE_EMOJI)


def cleanstring(line):
    return ''.join(x for x in line if x not in punctuation)


forbiddensymbols = ("[id", "[club", ".com", ".ru", "be")


def check_links(line):
    global forbiddensymbols
    for badword in forbiddensymbols:
        if line.find(badword) > -1:
            return False

    return True


numbers = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')


def check_numbers(line):
    if line[-1] in numbers:
        if line[-2] in numbers:
            return int(line[-2:])
        else:
            return int(line[-1])
    else:
        return -1


def convert_generated_to_text(generated):
    result = ""
    for frame in generated:
        result += frame + ' '

    return result


def try_to_generate(name_of_file):
    try:
        data = []
        with open(name_of_file, 'r') as file:
            for line in file:
                data.append(line)
        generator = mc.StringGenerator(data, 1)
        message = generator.generate(count=5, upper_first_letter=False)
        msg = convert_generated_to_text(message)
        return msg
    except mc.exceptions:
        return mc.exceptions


while True:
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            eventText = event.obj.text.lower()
            eventText = extract_emojis(eventText)
            print(eventText)
            if event.obj.peer_id != event.obj.from_id:
                # if there is no messages from this peer_id
                print("got some message")
                check_peer_id(event.obj.peer_id)
                print('peer')
                if eventText != "" and check_links(eventText):
                    print('pass')
                    append_file(event.obj.peer_id, cleanstring(eventText))
                    print('append')
                    messages_counter += 1
                    if messages_counter >= messages_limit:
                        messages_counter = 0
                        filename = str(event.obj.peer_id) + '.txt'
                        msg = try_to_generate(filename)
                        send_message(session_api, event.obj.peer_id, msg)
                if eventText[:25] == "[club178923582|@chattyai]":
                    if eventText.find("команды") > -1:
                        send_message(session_api, event.obj.peer_id, message=commands)
                    if eventText.find("рыгни") > -1:
                        send_message(session_api, event.obj.peer_id, message="*Рыгает*")
                    if eventText.find("анекдот") > -1:
                        send_message(session_api, event.obj.peer_id, message="Колобок повесился")
                    if eventText.find("заговоришь") > -1:
                        msg = str(messages_counter) + "/" + str(messages_limit)
                        send_message(session_api, event.obj.peer_id, msg)
                    if eventText.find("лимит") > -1:
                        set_limit(check_numbers(eventText))
                        send_message(session_api, event.obj.peer_id, message="Лимит теперь " + str(messages_limit))
                    if eventText.find("очистить") > -1:
                        if os.path.getsize(str(event.obj.peer_id) + '.txt') > 0:
                            create_or_clear_file(str(event.obj.peer_id) + '.txt')
                            table = {}
                            messages_counter = 0
                            send_message(session_api, event.obj.peer_id, message="Файл очищен")
                    if eventText.find("speak") > -1:
                        print('got cmd')
                        if messages_counter > 1:
                            print('pass x2')
                            filename = str(event.obj.peer_id) + '.txt'
                            msg = try_to_generate(filename)
                            send_message(session_api, event.obj.peer_id, msg)
                        else:
                            send_message(session_api, event.obj.peer_id, message='Мало данных')
            elif event.obj.peer_id == event.obj.from_id:
                send_message(session_api, event.obj.from_id, message="Каво?")
