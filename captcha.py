from PIL import Image, ImageDraw, ImageFont
import random
import string


def generate_captcha_image():
    # 定义图片大小及背景颜色
    image = Image.new('RGB', (120, 30), color=(73, 109, 137))

    # 使用系统自带字体，或指定字体文件路径
    font_path = "kumo.ttf"
    fnt = ImageFont.truetype(font_path, 40)
    d = ImageDraw.Draw(image)

    # 生成5位数的验证码文本
    captcha_text = ''.join(random.choices(string.digits, k=3))

    # 计算文本宽度
    text_width, _ = d.textsize(captcha_text, font=fnt)

    # 计算文本的起始位置使其水平居中
    text_x = (image.width - text_width) // 2
    text_y = (image.height - fnt.getsize(captcha_text)[1]) // 2

    d.text((text_x, text_y), captcha_text, font=fnt, fill=(255, 255, 0))

    # 添加干扰线条和噪点
    for _ in range(random.randint(3, 5)):
        start = (random.randint(0, image.width), random.randint(0, image.height))
        end = (random.randint(0, image.width), random.randint(0, image.height))
        d.line([start, end], fill=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

    for _ in range(100):
        xy = (random.randrange(0, image.width), random.randrange(0, image.height))
        d.point(xy, fill=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

    return image, captcha_text