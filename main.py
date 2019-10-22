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


while True:
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj.peer_id != event.obj.from_id:
                if event.obj.text.lower() == "[club178923582|@chattyai] команды":
                    send_message(session_api, event.obj.peer_id, message="Команды бота: \n \n 1) @chattyai рыгни")
                if event.obj.text.lower() == "[club178923582|@chattyai] рыгни":
                    send_message(session_api, event.obj.peer_id, message="*Рыгает*")
            if event.obj.peer_id == event.obj.from_id:
                send_message(session_api, event.obj.from_id, message="Каво?")
