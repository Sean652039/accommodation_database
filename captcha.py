from PIL import Image, ImageDraw, ImageFont
import random
import string


def generate_captcha_image():
    # Define image size and background color
    image = Image.new('RGB', (120, 30), color=(73, 109, 137))

    font_path = "kumo.ttf"
    fnt = ImageFont.truetype(font_path, 40)
    d = ImageDraw.Draw(image)

    # Generate 3-digit captcha text
    captcha_text = ''.join(random.choices(string.digits, k=3))

    # Calculate text width
    text_width, _ = d.textsize(captcha_text, font=fnt)

    # Calculate the starting position of the text to center it horizontally
    text_x = (image.width - text_width) // 2
    text_y = (image.height - fnt.getsize(captcha_text)[1]) // 2

    d.text((text_x, text_y), captcha_text, font=fnt, fill=(255, 255, 0))

    # Add distracting lines and noise
    for _ in range(random.randint(3, 5)):
        start = (random.randint(0, image.width), random.randint(0, image.height))
        end = (random.randint(0, image.width), random.randint(0, image.height))
        d.line([start, end], fill=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

    for _ in range(100):
        xy = (random.randrange(0, image.width), random.randrange(0, image.height))
        d.point(xy, fill=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

    return image, captcha_text