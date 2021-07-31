from pprint import pprint

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType, VkLongpollMode
from vk_api import VkUpload

token = "801eda3728281a02aef2e3da3c81cdb28934368c5316b84584f24b39555ead41379240479957aa11159cc"
# token = "6e7f30bb5e1751f236f038668c885878913282187ee41b0e83ec98ed75b26e11f38931baa4651c7291d4f"

# session.method('messages.send', {'user_id': user_id,  # отправка ответа
#                                       'message': text,
#                                       'random_id': 0, })

# vk.messages.send(user_id=event.user_id,
#                       message="было бы круто если бы ты принял заявку в друзья &#128522;",
#                       random_id=0)

# API-ключ созданный ранее
# Авторизуемся как сообщество
session = vk_api.VkApi(token=token)
vk = session.get_api()
# Работа с сообщениями

#

upload = VkUpload(session)


def token_user():
    token = '35e4445d780529a566993e033f6cd8031cb137a915bbd812bdc2cb1d1493dc9ec8c29fd88b4a727d48edf'
    session = vk_api.VkApi(token=token)
    vk = session.get_api()
    return vk


def uploaded_photo():
    """Выгрузка своего фото на сервер"""
    image = 'photo_2021-07-30_10-52-29.jpg'
    attachments = []
    upload_image = upload.photo_messages(photos=image)[0]
    attachments.append(f'photo{upload_image["owner_id"]}_{upload_image["id"]}')
    # pprint(upload_image)
    return attachments


attachments = ','.join(uploaded_photo())

# print(VkLongpollMode.GET_ATTACHMENTS)

# for i in longpoll_mode(mode = 2):
#
#
#     print(i)

# print(longpoll_mode)


longpoll = VkLongPoll(session)

while True:
    try:
        for event in longpoll.listen():
            # print(event.type)
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                # print(event.message['text'])
                if event.text:
                    print(event.type)
                    print(event.attachments)
                    # print(event.object)
                    if event.from_user:  # Если написали в ЛС
                        text = event.text.lower()
                        user = event.user_id
                        vk.messages.send(user_id=event.user_id,
                                         message=text,
                                         random_id=0)
                elif event.attachments:
                    print(event.raw)
                    print(event.from_user)
                    print(event.from_chat)
                    print(event.from_group)
                    print(event.from_me)
                    print(event.to_me)

                    print(event.attachments)
                    print(event.message_data)

                    print(event.message_id)
                    print(event.timestamp)
                    print(event.peer_id)
                    print(event.flags)
                    print(event.extra)
                    print(event.extra_values)
                    print(event.extra_values['title'])
                    print(event.type_id)

                    photo_data = event.attachments
                    # print(event.peer_id)

                    url = 'https://vk.com/melt_your_heart?z=photo222256657_457242741%2Falbum222256657_0'

                    # id сообщения
                    message_id = event.message_id
                    # print(message_id)

                    photo_id = photo_data['attach1']
                    photo_type = photo_data['attach1_type']

                    a = 'https://vk.com/id223318099?z=photo223318099_457368803%2Falbum223318099_0%2Frev'
                    b = 'https://vk.com/im?sel=-206157126&z=photo222256657_457242763%2Fmail1118992'
                    id_ = 222256657

                    # Данные фото
                    # data = token_user().photos.getById(photos=photo_id)
                    # print(data)

                    if event.from_user:  # Если написали в ЛС
                        text = event.text.lower()
                        user = event.user_id
                        answer = f'{photo_type}{photo_id}'
                        # print(answer)
                        # print(attachments)
                        # print(photo_data)
                        # print(answer)

                        # session.method('messages.send', {'user_id': user,  # отправка ответа
                        #                                  'message': 'How, are',
                        #                                  'random_id': 0,
                        #                                  'attachment':','.join(attachments),
                        #                                  })
                        # print(uploaded_photo())
                        # print(f'photo-206157126_{photo_id[10:]}')
                        vk.messages.send(user_id=event.user_id,
                                         message=message_id,
                                         attachment=attachments,
                                         # "sel=-206157126&z=photo222256657_457242759"
                                         random_id=0)
    except:
        pass
