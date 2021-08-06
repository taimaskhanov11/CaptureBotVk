import json
from pprint import pprint

from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from insert_in_photo import PhotoChanger

token = "801eda3728281a02aef2e3da3c81cdb28934368c5316b84584f24b39555ead41379240479957aa11159cc"
session = vk_api.VkApi(token=token)
vk = session.get_api()
id_group = 206157126
long_poll = VkBotLongPoll(session, id_group)

try:
    with open('photo_data.json', 'r', encoding='utf-8-sig') as ff:
        # if ff.read():
        photo_data = json.load(ff)
except:
    photo_data = {}
pprint(photo_data)


def run():
    global photo_data
    while True:
        try:
            for event in long_poll.listen():
                pprint(event)
                try:
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        if event.from_user:
                            # pprint(event.raw)#todo
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
                                                 message=f'Фото добавлено в базу| id photo {message_id}',
                                                 # attachment=f'photo{owner_id}_{photo_id}_{acces_key}',
                                                 # "sel=-206157126&z=photo222256657_457242759"
                                                 random_id=0)
                                # pprint('text')
                            else:
                                text = event.obj.text
                                if text.lower() == 'stop':
                                    photo_change = PhotoChanger()
                                    # photo_change.write_photo()
                                    photo_change.run()
                                    for i in photo_change.attached_img:
                                        vk.messages.send(peer_id=event.obj.peer_id,
                                                         # message=event.obj.text,
                                                         attachment=i,
                                                         random_id=0)
                                    vk.messages.send(peer_id=event.obj.peer_id,
                                                     message=f'Общая сумма {photo_change.total_sum} р\n'
                                                             f'{"=" * 30}',
                                                     # attachment=i,
                                                     random_id=0)
                                    photo_data = {}
                                    with open('photo_data.json', 'w', encoding='utf8') as ff:
                                        json.dump(photo_data, ff, indent=4, ensure_ascii=False)
                                elif text.lower() == 'start':
                                    vk.messages.send(peer_id=event.obj.peer_id,
                                                     message="Данные обнулены. Начинайте отправлять фото, редактируйте.\n"
                                                             "Как только все закончите отправляете команду stop\n"
                                                             "В ответ придут все фото с инфой и в самом конце общая сумма.",
                                                     # attachment=i,
                                                     random_id=0)
                                    photo_data = {}
                                    with open('photo_data.json', 'w', encoding='utf8') as ff:
                                        json.dump(photo_data, ff, indent=4, ensure_ascii=False)

                                elif 'del' in text.lower():
                                    photo_id = text.replace('del', '').strip()
                                    try:
                                        del photo_data[photo_id]
                                        vk.messages.send(peer_id=event.obj.peer_id,
                                                         message='Удалено из базы',
                                                         # "sel=-206157126&z=photo222256657_457242759"
                                                         random_id=0)
                                        with open('photo_data.json', 'w', encoding='utf8') as ff:
                                            json.dump(photo_data, ff, indent=4, ensure_ascii=False)


                                    except Exception as e:
                                        print(e)
                                        vk.messages.send(peer_id=event.obj.peer_id,
                                                         message='Ошибка',
                                                         # "sel=-206157126&z=photo222256657_457242759"
                                                         random_id=0)
                                    #
                                # pprint('else')

                    elif event.type == VkBotEventType.MESSAGE_EDIT:
                        # pprint(event.raw)#todo
                        if event.obj.attachments:
                            message_id = str(event.obj.conversation_message_id)
                            if message_id in photo_data:
                                photo_data[message_id]['text'] = event.obj.text
                                vk.messages.send(peer_id=event.obj.peer_id,
                                                 message=f"Данные id {message_id} в базе изменены изменены",
                                                 # attachment=f'photo{owner_id}_{photo_id}_{acces_key}',
                                                 # "sel=-206157126&z=photo222256657_457242759"
                                                 random_id=0)
                                with open('photo_data.json', 'w', encoding='utf8') as ff:
                                    json.dump(photo_data, ff, indent=4, ensure_ascii=False)
                    elif event.type == VkBotEventType.MESSAGE_DENY:
                        print('qwe')
                except:
                    vk.messages.send(peer_id=event.obj.peer_id,
                                     message=f"Ошибка в тексте",
                                     # attachment=f'photo{owner_id}_{photo_id}_{acces_key}',
                                     # "sel=-206157126&z=photo222256657_457242759"
                                     random_id=0)

        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    run()
# Получил старт, собираем все сообщения сохраняем conversation_message_id , ключи и адресс фото, если поменяет
# обновляем в базе по id  и меняем текс, после слова стоп кидаем в ответ данные с обновленными фото.
