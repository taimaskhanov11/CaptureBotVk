import json
from pprint import pprint

from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

token_user = 'b78e0ae0dc9ff9434b9d7dd073da692e9d39e4de158da2d50cf7d3d88e59e7085815dd5f3ce24ba6d8ea7'

token = "801eda3728281a02aef2e3da3c81cdb28934368c5316b84584f24b39555ead41379240479957aa11159cc"
session = vk_api.VkApi(token=token)
vk = session.get_api()
id_group = 206157126
long_poll = VkBotLongPoll(session, id_group)

# photo_data = {
#
# }
# a = 'photo{}_{}'

try:
    with open('photo_data.json', 'r', encoding='utf-8-sig') as ff:
        # if ff.read():
        photo_data = json.load(ff)
except:
    photo_data = {}
print(photo_data)


def run():
    while True:
        try:
            for event in long_poll.listen():
                pprint(event)

                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.from_user:
                        pprint(event.raw)
                        if event.obj.attachments:
                            photo_id = event.obj.attachments[0]['photo']['id']
                            owner_id = event.obj.attachments[0]['photo']['owner_id']
                            acces_key = event.obj.attachments[0]['photo']['access_key']
                            photo_urls = event.obj.attachments[0]['photo']['sizes']
                            photo_url = max(photo_urls, key=lambda x: x["height"])
                            message_id = str(event.obj.conversation_message_id)
                            print(message_id)
                            text = event.obj.text
                            photo_data[message_id] = {
                                'photo_id': photo_id,
                                'owner_id': owner_id,
                                'acces_key': acces_key,
                                'photo_url': photo_url['url'],
                                'text': text,
                            }
                            pprint(photo_url)
                            print(owner_id)
                            print(acces_key)
                            answer = f'photo{owner_id}_{photo_id}_acces_key'
                            print(answer)
                            with open('photo_data.json', 'w', encoding='utf8') as ff:
                                json.dump(photo_data, ff, indent=4, ensure_ascii=False)

                            vk.messages.send(peer_id=event.obj.peer_id,
                                             message='Фото добавлено в базу',
                                             # attachment=f'photo{owner_id}_{photo_id}_{acces_key}',
                                             # "sel=-206157126&z=photo222256657_457242759"
                                             random_id=0)
                            # pprint('text')
                        else:
                            text = event.obj.text
                            if text  == 'start':



                            vk.messages.send(peer_id=event.obj.peer_id,
                                             message=event.obj.text,
                                             # "sel=-206157126&z=photo222256657_457242759"
                                             random_id=0)
                            pprint('else')

                elif event.type == VkBotEventType.MESSAGE_EDIT:
                    pprint(event.raw)
                    if event.obj.attachments:
                        message_id = str(event.obj.conversation_message_id)
                        if message_id in photo_data:
                            photo_data[message_id]['text'] = event.obj.text
                            vk.messages.send(peer_id=event.obj.peer_id,
                                             message="Данные в базе изменены изменены",
                                             # attachment=f'photo{owner_id}_{photo_id}_{acces_key}',
                                             # "sel=-206157126&z=photo222256657_457242759"
                                             random_id=0)
                            with open('photo_data.json', 'w', encoding='utf8') as ff:
                                json.dump(photo_data, ff, indent=4, ensure_ascii=False)
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    run()
# Получил старт, собираем все сообщения сохраняем conversation_message_id , ключи и адресс фото, если поменяет
# обновляем в базе по id  и меняем текс, после слова стоп кидаем в ответ данные с обновленными фото.
