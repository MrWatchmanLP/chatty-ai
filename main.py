import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

token = "8ebd06e6b39901e266522e3bfb750bec56002534ff8d0f9faa8acc1b2a28422770ed7eca2e0dbe30e4ea5"
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 178923582)


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
messages_limit = 50
commands = "Команды бота:\n\n1)@chattyai рыгни\n2)@chattyai анекдот\n 3)@chattyai когда заговоришь"


def markov_blanket(text, order):
    result = {}

    for i in range(len(text) - order + 1):
        ngram = ""
        for off in range(order):
            ngram += text[i + off]

        if not ngram in result:
            result[ngram] = []
        if i < len(text) - order:
            result[ngram].append(text[i + order])
    return result


def markov_chain(blanket):
    keys = blanket.keys()
    ngram = random.choice(list(keys))
    new_text = ngram
    for i in range(100):
        try:
            nxt = random.choice(blanket[ngram])
            new_text += nxt
            ngram += nxt
            ngram = ngram[1:]
        except IndexError:
            break
    return new_text


def speak():
    new_text = markov_chain(markov_blanket(text, order))
    send_message(session_api, event.obj.peer_id, message=new_text)


def set_limit(limit):
    global messages_limit
    messages_limit = limit


def set_order(limit):
    global order
    order = limit


while True:
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            eventText = event.obj.text.lower()
            if event.obj.peer_id != event.obj.from_id:
                if eventText != "" and eventText[:25] != "[club178923582|@chattyai]":
                    text += eventText + "\n"
                    messages_counter += 1
                    if messages_counter >= messages_limit:
                        messages_counter = 0
                        speak()
                elif eventText[:25] == "[club178923582|@chattyai]":
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
                        if int(eventText[-1]) < 10:
                            set_limit(int(eventText[-1]))
                            send_message(session_api, event.obj.peer_id, message="Лимит теперь " + str(messages_limit))
                        else:
                            send_message(session_api, event.obj.peer_id, message="Лимит остался прежним")
                    if eventText.find("порядок") > -1:
                        if int(eventText[-1]) < 10:
                            set_order(int(eventText[-1]))
                            send_message(session_api, event.obj.peer_id, message="Порядок теперь " + str(order))
                        else:
                            send_message(session_api, event.obj.peer_id, message="Порядок остался прежним")
                    if eventText.find("очистить") > -1:
                        text = ""
                        messages_counter = 0
            elif event.obj.peer_id == event.obj.from_id:
                send_message(session_api, event.obj.from_id, message="Каво?")
