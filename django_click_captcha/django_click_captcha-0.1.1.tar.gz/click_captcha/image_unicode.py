import binascii
import random

from PIL import Image, ImageDraw, ImageFont


def gb2312():
    head = random.randint(0xB0, 0xCF)
    body = random.randint(0xA, 0xF)
    tail = random.randint(0, 0xF)
    val = (head << 8) | (body << 4) | tail
    try:
        return binascii.unhexlify(hex(val)[2:].encode('ascii')).decode('gb2312')
    except UnicodeDecodeError:
        return gb2312()


class ImageChar:
    def __init__(
            self,
            font_color=(0, 0, 0),
            height=50,
            char_number=6,
            font_path='STZHONGS.TTF',
            bg_color=(255, 255, 255, 255),
            font_size=30):
        """
        绘制汉字验证码图片定制的参数
        :param font_color: 字体颜色
        :param height: 生成验证码图片的高度
        :param char_number: 生成的汉字的个数
        :param font_path: 所采用的字体
        :param bg_color: 背景颜色
        :param font_size: 字体大小
        """

        # 总的验证码图片大小
        self.height = height
        self.size = (char_number * font_size, height)
        self.font_path = font_path
        self.bg_color = bg_color
        self.font_size = font_size
        self.char_number = char_number
        self.font_color = font_color
        # 生成字体对象
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        # 初始化一张空的验证码图片
        self.image = Image.new('RGBA', self.size, bg_color)

    def _draw_text(self, pos, txt, fill):
        """
        将文本绘制到空白的图片上面
        :param pos:
        :param txt:
        :param fill:
        :return:
        """
        draw = ImageDraw.Draw(self.image)
        draw.text(pos, txt, font=self.font, fill=fill)
        del draw

    def _random_point(self):
        """随机生成点，以便画线"""
        (width, height) = self.size
        return random.randint(0, width), random.randint(0, height)

    def _random_line(self, num):
        """
        随机画线， 进行识别干扰
        :param num: 划线的数目
        :return:
        """
        draw = ImageDraw.Draw(self.image)
        for i in range(0, num):
            draw.line([self._random_point(), self._random_point()], self.font_color)
        del draw

    @classmethod
    def choice_index(cls, number):
        num = random.randint(1, 3)
        return random.sample([i for i in range(0, number)], num)

    def random_chinese(self):
        start = 0  # 起始的位置
        point_list = []
        index_list = self.choice_index(self.char_number)
        # print(index_list)
        for i in range(0, self.char_number):
            char = gb2312()
            x = start + self.font_size * i
            # 随机上下波动
            p = random.randint(-5, 5)
            if i in index_list:
                temp_image = Image.new('RGBA', (self.font_size, self.height), self.bg_color)
                ImageDraw.Draw(temp_image).text((0, p), char, font=self.font, fill=(0, 0, 0))
                temp_image = temp_image.rotate(180)
                self.image.paste(temp_image, (x, 0))
                point_list.append(x)

            else:
                self._draw_text((x, p), char, (0, 0, 0))

        self._random_line(self.char_number)
        return point_list, self.image
