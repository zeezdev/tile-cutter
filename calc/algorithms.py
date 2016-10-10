
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


from PIL import Image, ImageDraw, ImageColor


def draw_floor(width, length, tile_width, tile_length, method):
    """X=length, Y=width
    :param width: width of floor (mm)
    :param length: length of floor (mm)
    :return: PIL.Image
    """
    scale_factor = 10

    size = (int(length/scale_factor), int(width/scale_factor))  # scale 10sm=100mm : 1px.
    tile_size = (int(tile_length/scale_factor), int(tile_width/scale_factor))

    image = Image.new('RGB', size, (255, 255, 255))
    draw = ImageDraw.Draw(image)

    if method == LAYING_METHOD_DIRECT:
        line_color = (255, 0, 0)
        line_width = 2

        # рисуем периметр
        draw.line((0, 0, size[0] - 1, 0), fill=line_color, width=line_width)
        draw.line((0, size[1]-1, size[0] - 1, size[1] - 1), fill=line_color, width=line_width)

        draw.line((0, 0, 0, size[1] - 1), fill=line_color, width=line_width)
        draw.line((size[0]-1, 0, size[0] - 1, size[1] - 1), fill=line_color, width=line_width)

        # рисуем плитки по length
        curr_x = 0
        while curr_x < size[0]:
            draw.line((curr_x, 0, curr_x, size[1]-1), fill=line_color, width=line_width)
            curr_x += tile_size[0]
        # рисуем плитки по width
        curr_y = 0
        while curr_y < size[1]:
            draw.line((0, curr_y, size[1]-1, curr_y), fill=line_color, width=line_width)
            curr_y += tile_size[1]
    else:
        raise Exception("Unknown method")

    return image


def save_image(image, path):
    import uuid
    import os

    filename = str(uuid.uuid4()) + ".png"

    fullname = os.path.join(path, filename)

    image.save(fullname, "PNG")

    return filename
