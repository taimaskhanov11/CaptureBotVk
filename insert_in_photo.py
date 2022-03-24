import json
import os
import re
import time

import requests
import vk_api
from PIL import Image, ImageDraw, ImageFont
from loguru import logger
from vk_api import VkUpload

# re.findall('(\d+)', '2BNKLOPY5T')
from database import Photo

token = "801eda3728281a02aef2e3da3c81cdb28934368c5316b84584f24b39555ead41379240479957aa11159cc"


class PhotoChanger:

    def __init__(self, owner_id):

        self.session = vk_api.VkApi(token=token)
        self.vk = self.session.get_api()
        self.upload = VkUpload(self.session)

        self.owner_id = owner_id
        self.count_obj = 0
        self.total_sum = 0
        self.photo_data = {}
        self.attached_img = []

    def run(self):
        self.open_json()
        # print(self.photo_data)
        for key, value in self.photo_data.items():
            text = value['text']
            if not text:
                continue
            name = value['photo_id']
            url = value['photo_url']
            photo = requests.get(url, stream=True).raw

            self.write_photo(photo, text, name)

            self.uploaded_photo(f'{name}.jpg')

        logger.info(f'Общая сумма {self.total_sum} рублей')

    def send_message(self, message):
        self.vk.messages.send(peer_id=self.owner_id,
                              message=message,
                              # attachment=i,
                              random_id=0)

    def send_attach_message(self, attachment, message_id):
        self.vk.messages.send(peer_id=self.owner_id,
                              message=message_id,
                              attachment=attachment,
                              random_id=0)

    def start(self):
        objects = Photo.get_all_photo(owner_id=self.owner_id)
        # print(self.photo_data)
        self.count_obj = len(objects)
        self.send_message(f'Загружено всего объектов {len(objects)}')

        for obj in objects:
            try:
                text = obj.text
                if not text:
                    continue
                name = f'{obj.unique_id}.jpg'
                photo_path = f'photos/{obj.unique_id}.jpg'
                url = obj.photo_url
                try:
                    photo = requests.get(url, stream=True, timeout=30).raw
                except Exception as e:
                    logger.critical(e)
                    continue
                self.write_photo(photo, text, photo_path)
                time.sleep(0.5)
                attach = self.uploaded_photo(photo_path)
                time.sleep(0.5)

                self.send_attach_message(attach, f'{obj.message_id}')
                self.del_photo_file(photo_path)
                obj.delete_instance()
                logger.debug("Файл удален из базы")
            except Exception as e:
                logger.critical(e)
                self.send_message(f'Ошибка! id photo {obj.message_id}')

        self.send_message(f'Общая сумма {self.total_sum}р \nВсего объектов {self.count_obj}\n{"=" * 30}')

        logger.info(f'Общая сумма {self.total_sum} рублей')

    def del_photo_file(self, photo_path):
        os.remove(photo_path)

    def uploaded_photo(self, image):
        """Выгрузка своего фото на сервер"""
        # image = 'photo_2021-07-28_22-42-55.jpg'
        # attachments = []
        upload_image = self.upload.photo_messages(photos=image)[0]
        # attachments.append(f'photo{upload_image["owner_id"]}_{upload_image["id"]}')
        # pprint(upload_image)
        attachments = f'photo{upload_image["owner_id"]}_{upload_image["id"]}'
        self.attached_img.append(attachments)
        return attachments

    def open_json(self):
        with open('photo_data.json', 'r', encoding='utf-8-sig') as ff:
            # if ff.read():
            self.photo_data = json.load(ff)

    def analyze_text(self, text):
        # text = '48 размер 1шт\n46 размер 4шт\n300р'
        word = ''
        if '(' in text:
            word = re.findall('\(.+\)', text, flags=re.M)[0]
            print(word)
            text = text.replace(word, '').strip()

        lst_text = text.split()
        # print(lst_text)

        # quantity = filter(lambda x: 'шт' in x, lst_text)

        quantity = re.findall('\d+шт|\d+\sшт', text)
        # print(quantity)
        # amount_str = lst_text[-1]
        # print(text)

        # re_amount = ['\d+\sр$', '\d+\sру', '\d+ру', '\d+р$']
        # find money
        amount_str = re.findall('\d+р$|\d+\sр$|\d+\sру|\d+ру', text)[0]
        # print(amount_str)
        # print(amount_str[0])

        # print(text)
        # print(lst_text)

        total_amount = int(''.join(re.findall('(\d+)', amount_str)))
        total_quantity = []
        # print(quantity)
        for q in quantity:
            # print(q)
            total_quantity.append(int(re.findall('(\d+)', q)[0]))
        sum_quantity = sum(total_quantity)
        # print(text)

        answer = f'Храпач\n{text} * {str(sum_quantity)}\n{word[1:-1]}'
        # print(text)
        # print(lst_text)
        # print(list(quantity))
        # print(amount_str)
        # print(total_amount)
        # print(total_quantity)
        # print(sum_quantity)
        # print(answer)

        self.total_sum += total_amount * sum_quantity
        # print(self.total_sum)
        return answer

    def write_photo(self, photo, text, path):
        with Image.open(photo) as im:
            text = self.analyze_text(text)
            x = 5
            y = 2
            size = im.size

            x, y = size
            end_size = x // 15

            counter_x = 20
            counter_y = 1
            x_end = x // counter_x
            y_end = y // counter_y
            # print(size)
            # print(end_size)

            # font = ImageFont.truetype('fonts/ofont.ru_Mononoki.ttf', size=end_size)
            font = ImageFont.truetype('fonts/fonts3/Roboto.ttf', size=end_size)
            offset = 3
            shadowColor = '#fff'

            x = x_end
            y = y - y_end
            d = ImageDraw.Draw(im)
            for off in range(2, 3):
                # move right
                d.text((x - off, y), text, font=font, fill=shadowColor)
                # move left
                d.text((x + off, y), text, font=font, fill=shadowColor)
                # move up
                d.text((x, y + off), text, font=font, fill=shadowColor)
                # move down
                d.text((x, y - off), text, font=font, fill=shadowColor)
                # diagnal left up
                d.text((x - off, y + off), text, font=font, fill=shadowColor)
                # diagnal right up
                d.text((x + off, y + off), text, font=font, fill=shadowColor)
                # diagnal left down
                d.text((x - off, y - off), text, font=font, fill=shadowColor)
                # diagnal right down
                d.text((x + off, y - off), text, font=font, fill=shadowColor)

                d.text((x, y), text, font=font, fill="black")
            # im.show()
            im.save(path)

        # with Image.open(photo) as im:
        #     draw_text = ImageDraw.Draw(im)
        #     # im.show()
        #     size = im.size
        #     end_size = size[0] // 15
        #     x, y = size
        #     counter_x = 15
        #     counter_y = 2
        #     x_end = x // counter_x
        #     y_end = y // counter_y
        #     # print(size)
        #     # print(end_size)
        #
        #     font = ImageFont.truetype('fonts/ofont.ru_Mononoki.ttf', size=end_size)
        #     draw_text.text(
        #         (x_end, y - y_end),
        #         text,
        #         fill='white',
        #         font=font
        #     )
        #     contour = x // 300
        #     print(contour)
        #     draw_text.text(
        #         (x_end + contour, y - y_end + contour),
        #         text,
        #         fill='black',
        #         font=font
        #     )
        #     # im.show()
        #     im.save(f'{name}.jpg')
        # # print(text)

    # def insert(self, photo_name, text):
    #     """Храпач
    #     48 размер 1шт
    #     46 размер 3шт
    #     4*500р"""
    #     pass


if __name__ == '__main__':
    owner_id = 424862770
    photo_change = PhotoChanger(owner_id)
    # photo_change.write_photo()
    photo_change.start()
    # analyze_text(123)

    # analyze_text()

# todo удалять в самом конце завершенные
