import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import mc

token = "8ebd06e6b39901e266522e3bfb750bec56002534ff8d0f9faa8acc1b2a28422770ed7eca2e0dbe30e4ea5"
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 178923582)
learning_data_local = []
counter = 0


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


text = ""
order = 5
messages_counter = 0

def markov_blanket(text, order):
    result = {}

    for i in range(len(text) - order + 1):
        ngram = ""
        for off in range(order):
            ngram += text[i+off]

        if not ngram in result:
            result[ngram] = []
        if i < len(text) - order:
            result[ngram].append(text[i+order])
    return result

def markov_chain(blanket):
    keys = blanket.keys()
    ngram = random.choice(list(keys))
    new_text = ngram
    cycles_counter = 0
    while True:
        try:
            nxt = random.choice(blanket[ngram])
            new_text += nxt
            ngram += nxt
            ngram = ngram[1:]
            cycles_counter += 1
            if cycles_counter == 5000:
                break
        except IndexError:
            break
    return new_text


while True:
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj.peer_id != event.obj.from_id:
                if event.obj.text.lower()[:25] != "[club178923582|@chattyai]":
                    text += event.obj.text + "\n"
                    messages_counter += 1
                if messages_counter >= 50:
                    new_text = markov_chain(markov_blanket(text, order))
                    send_message(session_api, event.obj.peer_id, message=new_text)
                if event.obj.text.lower()[:25] == "[club178923582|@chattyai]" and event.obj.text.lower().find(
                        "команды") > -1:
                    send_message(session_api, event.obj.peer_id,
                                 message="Команды бота: \n \n 1) @chattyai рыгни\n 2) @chattyai анекдот")
                if event.obj.text.lower()[:25] == "[club178923582|@chattyai]" and event.obj.text.lower().find(
                        "рыгни") > -1:
                    send_message(session_api, event.obj.peer_id, message="*Рыгает*")
                if event.obj.text.lower()[:25] == "[club178923582|@chattyai]" and event.obj.text.lower().find(
                        "анекдот") > -1:
                    send_message(session_api, event.obj.peer_id, message="Колобок повесился")
            if event.obj.peer_id == event.obj.from_id:
                send_message(session_api, event.obj.from_id, message="Каво?")
