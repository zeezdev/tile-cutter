import sys
from math import tan, tanh, sqrt, ceil
from django.conf import settings


LAYING_METHOD_DIRECT = 1
LAYING_METHOD_DIRECT_CENTER = 2
LAYING_METHOD_DIAGONAL = 3


def check_with_delimiters(l, tl, d, c):
    """ Уточняет необходимое количество плитки
    после добавления межплиточных разделителей.
    Если после добавления межплиточных расстояний
    суммарная длина больше покрываемой на целую плитку
    + 1 разделитель, то эта плитка не нужна.

    :param l: длина покрываемая плитками (mm).
    :param tl: размер плитки (mm).
    :param d: межплиточное расстояние (mm).
    :param c: количество необходимой плитки без разделителей.
    :return: Уточненное количество необходимой плитки для длины (l).
    """
    count = c
    if ((c * tl) + (d * c-1)) - l >= (tl + d):
        count -= 1

    return count


from PIL import Image, ImageDraw, ImageColor, ImageFont


__WATERMARK_FONT_SIZE = 60


def get_font(size):
    return ImageFont.truetype(
        settings.DRAWING_WATERMARK_FONT,
        size=size
    )

def add_text_watermark(text):

    def decorator(func):
        def wrapper(*args):
            image = func(*args)

            watermark = Image.new('RGBA', size=image.size, color=0)
            # watermark = Image.new('RGBA', size=(image.width, 64), color=0)
            draw = ImageDraw.Draw(watermark)
            font = get_font(60)
            tw = None
            th = None
            while True:
                tw, th = draw.textsize(text, font=font)
                if tw+10 < image.size[0] and th+10 < image.size[1]:
                    break
                font = get_font(font.size-2)

            draw.text(
                (image.width/2 - tw/2, image.height/2 - th/2),
                text,
                fill=(0, 0, 0, 128),
                font=font
            )

            # image.paste(watermark, box=(0, 15), mask=watermark)
            return Image.alpha_composite(image, watermark)
            # return image

        return wrapper
    return decorator


def add_background(color):
    def decorator(func):
        def wrapper(*args):
            image = func(*args)
            bg = Image.new('RGBA', (image.width, image.height), color)
            bg.paste(image, mask=image)

            return bg
        return wrapper

    return decorator


# @add_background(color=(255, 255, 255, 255))
@add_text_watermark(settings.DRAWING_WATERMARK_TEXT)
def draw_floor(width, length, tile_width, tile_length, method=LAYING_METHOD_DIRECT):
    """X=length, Y=width
    :param width: width of floor (mm)
    :param length: length of floor (mm)
    :param method: mothod of tile laying.
    :return: PIL.Image
    """
    scale_factor = 9  # TODO: need compute this

    size = (sys.maxsize, sys.maxsize)
    while any(s > 1000 for s in size):
        scale_factor += 1
        size = (int(length/scale_factor), int(width/scale_factor))  # scale 10sm=100mm : 1px.

    tile_size = (int(tile_length/scale_factor), int(tile_width/scale_factor))

    center_x = size[0] / 2
    center_y = size[1] / 2

    image = Image.new('RGBA', size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)

    line_color = (255, 0, 0, 255)
    line_width = 1

    # рисуем периметр
    draw.line((0, 0, size[0] - 1, 0), fill=line_color, width=line_width)
    draw.line((0, size[1] - 1, size[0] - 1, size[1] - 1), fill=line_color, width=line_width)

    draw.line((0, 0, 0, size[1] - 1), fill=line_color, width=line_width)
    draw.line((size[0] - 1, 0, size[0] - 1, size[1] - 1), fill=line_color, width=line_width)

    if method == LAYING_METHOD_DIRECT:
        # рисуем плитки по length
        curr_x = 0
        while curr_x < size[0]:
            draw.line((curr_x, 0, curr_x, size[1]-1), fill=line_color, width=line_width)
            curr_x += tile_size[0]
        # рисуем плитки по width
        curr_y = 0
        while curr_y < size[1]:
            draw.line((0, curr_y, size[0]-1, curr_y), fill=line_color, width=line_width)
            curr_y += tile_size[1]
    elif method == LAYING_METHOD_DIRECT_CENTER:  # TODO: simplify - start from outside.
        # рисуем полосы по length (x)
        curr_x = size[0]/2 + tile_size[0]/2
        draw.line((curr_x, 0, curr_x, size[1]-1), fill=line_color, width=line_width)
        while curr_x >= 0:
            curr_x -= tile_size[0]
            draw.line((curr_x, 0, curr_x, size[1] - 1), fill=line_color, width=line_width)

        curr_x = size[0]/2 + tile_size[0]/2
        draw.line((curr_x, 0, curr_x, size[1] - 1), fill=line_color, width=line_width)
        while curr_x <= size[0]:
            curr_x += tile_size[0]
            draw.line((curr_x, 0, curr_x, size[1] - 1), fill=line_color, width=line_width)

        # рисуем полосы по width (y)
        curr_y = size[1] / 2 + tile_size[1] / 2
        draw.line((0, curr_y, size[0] - 1, curr_y), fill=line_color, width=line_width)
        while curr_y >= 0:
            curr_y -= tile_size[1]
            draw.line((0, curr_y, size[0] - 1, curr_y), fill=line_color, width=line_width)

        curr_y = size[1] / 2 + tile_size[1] / 2
        draw.line((0, curr_y, size[0] - 1, curr_y), fill=line_color, width=line_width)
        while curr_y <= size[1]:
            curr_y += tile_size[0]
            draw.line((0, curr_y, size[0] - 1, curr_y), fill=line_color, width=line_width)
    elif method == LAYING_METHOD_DIAGONAL:
        # представим наклонную грань плитки гипотенузой прамоугольного треугольника.
        # находим длину прилежащего катета через угол (45) и длину противолежащего.
        b = center_y
        alpha = 45.0
        a = b * tanh(alpha)

        # находим диагональ плитки
        if tile_width == tile_length:
            d = sqrt(2) * tile_width
        else:
            d = sqrt(tile_length**2 + tile_width**2)
        d /= scale_factor
        d05 = d/2

        # находим выступ за границами объекта для начала рисования наклонных линий:
        # сдвигаемся от центра на полплитки + суммарную длину диагоналей целых плиток,
        # добавляем длину прилежащего катета (a).
        m = ((ceil((center_x-d05)/d) * d) + d05) - center_x
        m = -(m+d*2)
        curr_x = m

        while curr_x < size[0] or curr_x-a < size[0]:
            draw.line((curr_x-a, 0, curr_x+a, size[1]-1), fill=line_color, width=line_width)
            draw.line((curr_x + a, 0, curr_x - a, size[1] - 1), fill=line_color, width=line_width)
            curr_x += d

        # curr_x = m
        # while curr_x < size[0] or curr_x - a < size[0]:
        #     draw.line((curr_x + a, 0, curr_x - a, size[1] - 1), fill=line_color, width=line_width)
        #     curr_x += d
    else:
        raise Exception("Unknown drawing method")

    return image


@add_text_watermark(settings.DRAWING_WATERMARK_TEXT)
def draw_walls(width, length, height, tile_length, tile_height):
    scale_factor = 9.0  # TODO: need compute this
    perimetr = (length+width)*2

    size = (sys.maxsize, sys.maxsize)
    while any(s > 1000 for s in size):
        scale_factor += 1.0
        size = (int(perimetr/scale_factor), int(width/scale_factor))  # scale 10sm=100mm : 1px.

    tile_size = (int(tile_length/scale_factor), int(tile_height/scale_factor))

    image = Image.new('RGBA', size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)

    # single method
    line_color = (255, 0, 0, 255)
    side_color = (0, 0, 255, 255)
    line_width = 1

    # рисуем контур развертки всех стенок
    draw.line((0, 0, size[0] - 1, 0), fill=line_color, width=line_width)
    draw.line((0, size[1]-1, size[0] - 1, size[1] - 1), fill=line_color, width=line_width)

    draw.line((0, 0, 0, size[1] - 1), fill=line_color, width=line_width)
    draw.line((size[0]-1, 0, size[0] - 1, size[1] - 1), fill=line_color, width=line_width)

    laying_direction_y = -1

    # рисуем плитки по length
    curr_x = 0
    while curr_x < size[0]:
        draw.line((curr_x, 0, curr_x, size[1]-1), fill=line_color, width=line_width)
        curr_x += tile_size[0]

    # рисуем плитки по height
    curr_y = 0
    while curr_y < size[1]:
        draw.line((0, size[1] - curr_y, size[0]-1, size[1] - curr_y), fill=line_color, width=line_width)

        curr_y += tile_size[1]

    # рисуем стыки стен
    draw.line((length/scale_factor, 0, length/scale_factor, size[1]-1), fill=side_color, width=2)
    draw.line(((length+width) / scale_factor, 0, (length+width) / scale_factor, size[1] - 1), fill=side_color, width=2)
    draw.line(((2*length+width) / scale_factor, 0, (2*length+width) / scale_factor, size[1] - 1), fill=side_color, width=2)

    return image


def save_image(image, path):
    import uuid
    import os

    filename = str(uuid.uuid4()) + ".png"

    fullname = os.path.join(path, filename)

    image.save(fullname, "PNG")

    return filename


def calc_cost(count, price):
    """Вычисляет необходимую стоимость простым умножением.
    Точность 2 знака.
    :param count:
    :param price: price of one tile.
    :return:
    """
    return round(count * price, 2)
