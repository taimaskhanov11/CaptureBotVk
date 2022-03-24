import sys
from pathlib import Path

from loguru import logger
from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from database import Photo
from insert_in_photo import PhotoChanger

token = "801eda3728281a02aef2e3da3c81cdb28934368c5316b84584f24b39555ead41379240479957aa11159cc"
session = vk_api.VkApi(token=token)
vk = session.get_api()
id_group = 206157126
long_poll = VkBotLongPoll(session, id_group)

logger.remove()
logger.add(
    sink=sys.stderr,
    level="TRACE",
    enqueue=True,
    diagnose=True,
)
logger.add(
    sink=Path("logs/main.log"),
    level="TRACE",
    enqueue=True,
    encoding="utf-8",
    diagnose=True,
    rotation="5MB",
    compression="zip",
)


def send_message(peer_id, message):
    vk.messages.send(peer_id=peer_id,
                     message=message,
                     # attachment=f'photo{owner_id}_{photo_id}_{acces_key}',
                     # "sel=-206157126&z=photo222256657_457242759"
                     random_id=0)


def run():
    while True:
        try:
            for event in long_poll.listen():
                # pprint(event)
                try:
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        if event.from_user:
                            # pprint(event.raw)  # todo
                            user_id = event.obj.from_id
                            if event.obj.attachments:
                                photo_id = event.obj.attachments[0]['photo']['id']
                                owner_id = event.obj.attachments[0]['photo']['owner_id']
                                access_key = event.obj.attachments[0]['photo']['access_key']
                                photo_urls = event.obj.attachments[0]['photo']['sizes']
                                photo_url = max(photo_urls, key=lambda x: x["height"])
                                message_id = str(event.obj.conversation_message_id)
                                text = event.obj.text

                                Photo.create(unique_id=int(f'{owner_id}{message_id}'),
                                             photo_id=photo_id,
                                             owner_id=owner_id,
                                             message_id=message_id,
                                             access_key=access_key,
                                             photo_url=photo_url['url'],
                                             text=text)

                                print('message_id', message_id)
                                print('user_id', user_id)
                                send_message(user_id, f'Фото добавлено в базу| id photo {message_id}')

                            else:
                                text = event.obj.text
                                if text.lower() == 'stop':
                                    photo_change = PhotoChanger(owner_id=event.obj.from_id)
                                    # photo_change.write_photo()
                                    photo_change.start()

                                elif text.lower() == 'start':
                                    send_message(user_id, "Данные обнулены. Начинайте отправлять фото, редактируйте.\n"
                                                          "Как только все закончите отправляете команду stop\n"
                                                          "В ответ придут все фото с инфой и в самом конце общая сумма.")
                                elif 'del' in text.lower():
                                    owner_id = user_id
                                    message_id = text.replace('del', '').strip()
                                    try:
                                        unique_id = int(f'{owner_id}{message_id}')
                                        obj = Photo.get_photo(unique_id)
                                        if obj:
                                            obj.delete_instance()
                                            send_message(user_id, 'Удалено из базы')
                                        else:
                                            send_message(user_id, 'Нету в базе')

                                    except Exception as e:
                                        print(e)
                                        send_message(user_id, 'Ошибка')
                                    #
                                # pprint('else')

                    elif event.type == VkBotEventType.MESSAGE_EDIT:
                        # pprint(event.raw)#todo
                        # print(event.obj.conversation_message_id)
                        # print(type(event.obj.conversation_message_id))
                        if event.obj.attachments:
                            message_id = event.obj.conversation_message_id
                            owner_id = event.obj.from_id
                            message_text = event.obj.text
                            unique_id = int(f'{owner_id}{message_id}')
                            photo = Photo.get_photo(unique_id)
                            if photo:
                                photo.text = message_text
                                photo.save()
                                send_message(owner_id, f"Данные id {message_id} в базе изменены изменены")

                    elif event.type == VkBotEventType.MESSAGE_DENY:
                        print('qwe')
                except Exception as e:
                    logger.critical(e)
                    send_message(event.obj.from_id, 'Ошибка в тексте')

        except Exception as e:
            logger.critical(e)
            pass


if __name__ == '__main__':
    run()
# Получил старт, собираем все сообщения сохраняем conversation_message_id , ключи и адресс фото, если поменяет
# обновляем в базе по id  и меняем текс, после слова стоп кидаем в ответ данные с обновленными фото.
# todo добавить многопроцесорность
