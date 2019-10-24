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


messages_counter = 0
messages_limit = 50
commands = "Команды бота:\n\n1)@chattyai рыгни\n2)@chattyai анекдот\n3)@chattyai когда заговоришь\n4)@chattyai " \
           "лимит\n5)@chattyai предложение\n6)@chattyai очистить "


class markov:
    def __init__(self, markov_order):
        self.order = markov_order
        self.group_size = self.order + 1
        self.file = open("file.txt", "w")
        self.file.close()
        self.text = None
        self.graph = {}
        return

    def train(self):
        self.file = open("file.txt", "r")
        self.text = self.file.read().split()
        self.text = self.text + self.text[:self.order]

        for i in range(0, len(self.text) - self.group_size):

            key = tuple(self.text[i:i + self.order])
            value = self.text[i + self.order]

            if key in self.graph:
                self.graph[key].apped(value)
            else:
                self.graph[key] = [value]
        return

    def add_to_file(self, line):
        self.file = open("file.txt", "a")
        self.file.write(line + "\n")
        self.file.close()

    def clear_file(self):
        self.file = open("file.txt", "w")
        self.file.close()

    def generate(self, length):
        index = random.randint(0, len(self.text) - self.order)
        result = self.text[index:index + self.order]

        for i in range(length):
            state = tuple(result[len(result) - self.order:])
            next_word = random.choice(self.graph[state])
            result.append(next_word)
        self.file.close()
        return " ".join(result[self.order:])


mark = markov(5)
sentence_length = 10


def speak():
    mark.train()
    sentence = mark.generate(sentence_length)
    send_message(session_api, event.obj.peer_id, sentence)


def set_limit(limit):
    global messages_limit
    messages_limit = limit


def set_sentence_length(length):
    global sentence_length
    sentence_length = length


while True:
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            eventText = event.obj.text.lower()
            if event.obj.peer_id != event.obj.from_id:
                if eventText != "" and eventText[:25] != "[club178923582|@chattyai]":
                    mark.add_to_file(eventText)
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
                        if int(eventText[-2]) < 50:
                            set_limit(int(eventText[-2:]))
                            send_message(session_api, event.obj.peer_id, message="Лимит теперь " + str(messages_limit))
                        else:
                            send_message(session_api, event.obj.peer_id, message="Лимит остался прежним")
                    if eventText.find("предложение") > -1:
                        if int(eventText[-2]) < 50:
                            set_sentence_length(int(eventText[-2:]))
                            send_message(session_api, event.obj.peer_id, message="Длина теперь" + str(sentence_length))
                        else:
                            send_message(session_api, event.obj.peer_id, message="Длина осталась прежней")
                    if eventText.find("очистить") > -1:
                        mark.clear_file()
                        messages_counter = 0
            elif event.obj.peer_id == event.obj.from_id:
                send_message(session_api, event.obj.from_id, message="Каво?")
