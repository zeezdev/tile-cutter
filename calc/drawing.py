#!/usr/bin/env python

import os
from abc import ABCMeta, abstractmethod
from PIL import Image, ImageDraw, ImageFont
from copy import deepcopy
from math import ceil, floor

if __name__ == "__main__":
    # DRAWING
    DRAWING_WATERMARK_TEXT = "www.tcutter.ru"
    DRAWING_WATERMARK_FONT = "/home/zeez/work/cutter/static/fonts/arial.ttf"
else:
    from django.conf import settings
    DRAWING_WATERMARK_TEXT = settings.DRAWING_WATERMARK_TEXT
    DRAWING_WATERMARK_FONT = settings.DRAWING_WATERMARK_FONT

color = (120, 120, 120, 255)
color_cutted = (255, 0, 0, 255)


__WATERMARK_FONT_SIZE = 60

def get_font(size):
    return ImageFont.truetype(
        DRAWING_WATERMARK_FONT,
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


class Object(metaclass=ABCMeta):

    def __init__(self):
        self.offset = (0, 0)

    @abstractmethod
    def draw(self, canvas, start_pos): pass

    @staticmethod
    def _draw_line(d, x0, y0, x1, y1, color=None):
        """
        :param d:
        :type d: ImageDraw
        :param x0:
        :param y0:
        :param x1:
        :param y1:
        :return:
        """
        d.line((x0, y0, x1, y1), fill=color or (80, 80, 80, 255), width=1)

    @abstractmethod
    def draw_contour_out(self, canvas, start_pos, length): pass

    @abstractmethod
    def get_size(self):
        """
        :return:
        :rtype: Size
        """
        pass


class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __str__(self):
        return "{}x{}".format(self.width, self.height)


class Canvas:
    def __init__(self, w, h, scale_factor=None, max_size=None):
        """
        :param w:
        :param h:
        :param scale_factor:
        :param max_size:
        :type Size
        """
        self._width = w
        self._height = h
        if scale_factor:
            self._scale_factor = scale_factor
        elif max_size:
            sf = 1.0
            while True:
                change = False
                if max_size.width * sf > self._width or max_size.height * sf > self._height:
                    sf *= 0.9
                    change = True

                if max_size.width * (sf * 1.0625) <= self._width and max_size.height * (sf * 1.0625) <= self._height:
                    sf *= 1.0625
                    change = True

                if not change:
                    break

            self._scale_factor = sf
            print("Scale factor auto set to: %f" % sf)
        else:
            raise Exception("need scale_factor or max_size")

        self.im = Image.new(
            'RGBA',
            (self._width, self._height),
            (255, 255, 255, 255)
        )

    def get_draw(self):
        return ImageDraw.Draw(self.im)

    def save_to_file(self, filename):
        self.im.save(filename, "PNG")

    def to_pixels(self, value):
        """Convert mm in to pixels.
        :param value: value in mm
        :type value: float
        :return: scaled value in pixels of canvas
        :rtype: int
        """
        return int(self._scale_factor * value)


class Tile(Object):
    def __init__(self, w, h, start_x=None, start_y=None, max_x=None, max_y=None):
        super(Tile, self).__init__()
        self.width = w
        self.height = h
        self.start_x = start_x
        self.start_y = start_y
        self.max_x = max_x
        self.max_y = max_y

    def draw(self, canvas, start_pos):
        d = canvas.get_draw()
        wpix = canvas.to_pixels(self.width)
        hpix = canvas.to_pixels(self.height)

        sp = start_pos

        if self.max_x is not None:
            wpix = self.max_x
        if self.max_y is not None:
            hpix = self.max_y

        if self.start_x is not None:
            wpix = (wpix - self.start_x)
            # sp.x += self.start_x
        if self.start_y is not None:
            hpix = (hpix - self.start_y)
            sp.y += self.start_y

        # if wpix <= 0:
        #     print("[WRN]: tile width <= 0")
        #     return

        # fill shape
        d.polygon([
            (sp.x, sp.y),
            (sp.x + wpix, sp.y),
            (sp.x + wpix, sp.y + hpix),
            (sp.x, sp.y + hpix)
        ], fill="#b9cbda")

        # top line
        if self.start_y is None:
            self._draw_line(d, sp.x, sp.y, sp.x + wpix, sp.y, color=color)
        else:
            self._draw_line(d, sp.x, sp.y, sp.x + wpix, sp.y, color=color_cutted)

        # left line
        if self.start_x is None:
            self._draw_line(d, sp.x, sp.y + hpix, sp.x, sp.y, color=color)
        else:
            self._draw_line(d, sp.x, sp.y + hpix, sp.x, sp.y, color=color_cutted)

        # right line
        if self.max_x is None:
            self._draw_line(d, sp.x + wpix, sp.y, sp.x + wpix, sp.y + hpix, color=color)
        else:
            self._draw_line(d, sp.x + wpix, sp.y, sp.x + wpix, sp.y + hpix, color=color_cutted)

        # bottom line
        if self.max_y is None:
            self._draw_line(d, sp.x + wpix, sp.y + hpix, sp.x, sp.y + hpix, color=color)
        else:
            self._draw_line(d, sp.x + wpix, sp.y + hpix, sp.x, sp.y + hpix, color=color_cutted)

    def draw_contour_out(self, canvas, start_pos, length): pass

    def get_size(self):
        return Size(self.width, self.height)


class DrawSettings:
    def __init__(self, cc):
        self.contour_color = cc


class Position:
    def __init__(self, x=0, y=0):
        """
        :param x: offset by X-coord in pixels
        :param y: offset by Y-coord in pixels
        """
        self.x = x
        self.y = y


class WallTilesOptions:
    def __init__(self, w, h, d, sx=None, sy=None, mx=None, my=None):
        """
        :param w: tile width in mm
        :param h: tile height in mm
        :param d: delimiter in mm
        :param sx: start from by X-coord in mm
        :param sy: start from by Y-coord in mm
        :param mx:
        :param my:
        """
        self.width = w
        self.height = h
        self.delimiter = d
        self.start_x = sx
        self.start_y = sy
        self.max_x = mx
        self.max_y = my


class Wall(Object):
    def __init__(self, w, h, tile, options=None):
        """
        :param w:
        :param h:
        :param tile:
        :type tile: WallTilesOptions
        :param options:
        """
        super(Wall, self).__init__()

        # Validation

        if 'door_width' in options and options['door_width'] is not None:
            assert options['door_width'] <= w
        if 'door_height' in options and options['door_height'] is not None:
            assert options['door_height'] <= h

        if w <= 0:
            raise Exception("w: invalid value")
        if h <= 0:
            raise Exception("h: invalid value")

        # -----------------

        self.height = h
        self.width = w

        self._tile_opt = tile
        d = self._tile_opt.delimiter
        tw = self._tile_opt.width
        twd = tw+d  # длина плитки с последующим! разделителем
        th = self._tile_opt.height
        # thd = th+d
        tsx = (self._tile_opt.start_x or 0)
        clear_width = self.width - (tsx + d)

        self._tile_opt.max_x = None
        ceil_num = ceil(clear_width/twd)

        if ceil_num * twd > clear_width:
            self._tile_opt.max_x = tw - ((ceil_num * twd) - clear_width)

        self._tile_opt.max_y = None

        self._opt = (options or {})

    def get_tile_options(self):
        return self._tile_opt

    def get_size(self):
        return Size(self.width, self.height)

    def draw(self, canvas, start_pos, y_direction=-1):
        """
        :param canvas:
        :type canvas: Canvas
        :param start_pos:
        :type start_pos: Position
        :param y_direction:  1-сверху вниз/-1-снизу вверх
        :return:
        """
        d = canvas.get_draw()
        wpix = canvas.to_pixels(self.width)
        hpix = canvas.to_pixels(self.height)
        sp = start_pos

        # Рисуем общий контур стены
        self._draw_line(d, sp.x, sp.y, sp.x + wpix, sp.y)
        self._draw_line(d, sp.x + wpix, sp.y, sp.x + wpix, sp.y + hpix)
        self._draw_line(d, sp.x + wpix, sp.y + hpix, sp.x, sp.y + hpix)
        self._draw_line(d, sp.x, sp.y + hpix, sp.x, sp.y)

        # Рисуем внешний контур для размеров
        if 'contour_out' in self._opt:
            length = 15
            if 'length' in self._opt['contour_out']:
               length = int(self._opt['contour_out']['length'])
            self.draw_contour_out(canvas, start_pos, length)  # TODO: away from here...

        # Рисуем плитки
        tile_wpix = canvas.to_pixels(self._tile_opt.width)
        tile_hpix = canvas.to_pixels(self._tile_opt.height)
        tile_dpix = canvas.to_pixels(self._tile_opt.delimiter) or 1

        tile = Tile(self._tile_opt.width, self._tile_opt.height)

        local = Position()
        first_x = True
        first_y = True
        tiles_count = 0

        is_door_draw = 'door_width' in self._opt and 'door_height' in self._opt \
                       and self._opt['door_width'] is not None and self._opt['door_height'] is not None
        center = Position(sp.x + wpix / 2, sp.y + hpix / 2)  # цетр стены с учетом началного положения

        if is_door_draw:
            door_size = Size(
                canvas.to_pixels(self._opt['door_width']),
                canvas.to_pixels(self._opt['door_height'])
            )
            door_pos = Position(center.x - (door_size.width/2), sp.y + hpix - door_size.height)

        while True:
            local.y += tile_dpix  # ряд начинается с разделителя

            start_y = None
            max_y = None

            if local.y + tile_hpix > hpix - tile_dpix:  # целая плитка не входит
                if y_direction == 1:  # подрезка снизу
                    max_y = (hpix - tile_dpix) - local.y
                elif y_direction == -1:  # подрезка сверху
                    start_y = (local.y + tile_hpix) - (hpix - tile_dpix)
                else:
                    raise Exception("invalid y_direction")

            while True:
                local.x += tile_dpix  # ряд начинается с разделителя

                start_x = None
                max_x = None

                # если в настройках стены есть сдвиги добавляем их первому ряду плиток
                if self._tile_opt.start_x and first_x:
                    start_x = canvas.to_pixels(self._tile_opt.start_x)
                if self._tile_opt.start_y and first_y:
                    start_y = canvas.to_pixels(self._tile_opt.start_y)

                tmp = (local.x + tile_wpix + tile_dpix)-wpix
                if tmp > 0:
                    max_x = tile_wpix - ((local.x + tile_wpix + tile_dpix) - wpix)

                tile.start_x = start_x
                tile.start_y = start_y
                tile.max_x = max_x
                tile.max_y = max_y

                if y_direction == 1:
                    pos = Position(
                        sp.x + local.x,
                        sp.y + local.y
                    )
                elif y_direction == -1:
                    pos = Position(
                        sp.x + local.x,
                        sp.y + hpix - (local.y + tile_hpix)
                    )
                else:
                    raise Exception("invalid y_direction")

                tile_pos = PositionalObject(tile, pos)
                if not is_door_draw or not tile_pos.is_in_area(door_pos, door_size, canvas):
                    tile_pos.draw(canvas)

                if tile.start_x is None:  # если плитка не подрезка с предыдущей стены
                    tiles_count += 1

                if max_x is not None and max_x > 0:
                    local.x += tile_dpix
                    local.x += max_x - (start_x or 0)
                    self._tile_opt.max_x = max_x / canvas._scale_factor  # запомним подрезку последней плитки
                else:
                    local.x += tile_wpix - (start_x or 0)

                # if tile_dpix > 2:
                #     x += tile_dpix-2
                if local.x >= wpix:
                    break

                first_x = False

            # ---------
            local.x = 0
            first_x = True

            if start_y is not None:
                local.y += tile_hpix  # -start_y
            else:
                local.y += tile_hpix

            if local.y >= hpix:
                break

        # Draw the door
        if 'door_width' in self._opt and 'door_height' in self._opt \
                and self._opt['door_width'] is not None and self._opt['door_height'] is not None:
            door_width_half_px = canvas.to_pixels(self._opt['door_width'])/2
            door_height_px = canvas.to_pixels(self._opt['door_height'])

            # Рисование двери заливкой
            # draw = canvas.get_draw()
            d.polygon([
                (center.x-door_width_half_px, sp.y+hpix),
                (center.x-door_width_half_px, sp.y+hpix-door_height_px),
                (center.x+door_width_half_px, sp.y+hpix-door_height_px),
                (center.x+door_width_half_px, sp.y+hpix),
            ], fill="#fff")

            # Рисование двери линиями
            self._draw_line(d, center.x - door_width_half_px, sp.y + hpix,
                            center.x - door_width_half_px, sp.y + hpix - door_height_px, color=color_cutted)
            self._draw_line(d, center.x + door_width_half_px, sp.y + hpix,
                            center.x + door_width_half_px, sp.y + hpix - door_height_px, color=color_cutted)
            self._draw_line(d, center.x - door_width_half_px, sp.y + hpix - door_height_px,
                            center.x + door_width_half_px, sp.y + hpix - door_height_px, color=color_cutted)

        # TODO: other objects ...


        bound_box_in_canvas = (
            sp.x,  # start X
            sp.y,  # start Y
            wpix,  # width
            hpix,  # height
        )
        print("tiles count=%d" % tiles_count)

        return bound_box_in_canvas

    def draw_contour_out(self, canvas, start_pos, length):
        d = canvas.get_draw()
        wpix = canvas.to_pixels(self.width)
        hpix = canvas.to_pixels(self.height)
        sp = start_pos

        self._draw_line(d, sp.x, sp.y, sp.x - length, sp.y)
        self._draw_line(d, sp.x, sp.y, sp.x, sp.y - length)

        self._draw_line(d, sp.x+wpix, sp.y, sp.x+wpix + length, sp.y)
        self._draw_line(d, sp.x+wpix, sp.y, sp.x+wpix, sp.y - length)

        self._draw_line(d, sp.x, sp.y+hpix, sp.x - length, sp.y + hpix)
        self._draw_line(d, sp.x, sp.y+hpix, sp.x, sp.y + hpix + length)

        self._draw_line(d, sp.x + wpix, sp.y + hpix, sp.x + wpix + length, sp.y + hpix)
        self._draw_line(d, sp.x + wpix, sp.y + hpix, sp.x + wpix, sp.y + hpix + length)


class PositionalObject:
    def __init__(self, obj, pos):
        """
        :param obj:
        :type obj: Object
        :param pos:
        :type pos: Position
        """
        self._obj = obj
        if not isinstance(pos, Position):
            raise Exception("not Position type")
        self.pos = pos

    def draw(self, canvas):
        self._obj.draw(canvas, self.pos)

    def is_in_area(self, area_pos, area_size, canvas):
        """
        :param area_pos:
        :type area_pos: Position
        :param area_size:
        :type area_size: Size
        :return:
        """
        x0 = self.pos.x
        x1 = self.pos.x + canvas.to_pixels(self._obj.get_size().width)
        y0 = self.pos.y
        y1 = self.pos.y + canvas.to_pixels(self._obj.get_size().height)
        return x0 > area_pos.x and x1 < area_pos.x + area_size.width \
               and y0 > area_pos.y and y1 < area_pos.y + area_size.height



class Draw:
    def draw(self, canvas, objects):
        """
        :param canvas:
        :param objects:
        :type objects: list of PositionalObject
        :return:
        """
        # canvas = None  # TODO: make canvas (PILLOW)
        for obj in objects:
            obj.draw(canvas)

    def draw_wm(self, canvas):
        image = canvas.im
        text = DRAWING_WATERMARK_TEXT

        watermark = Image.new('RGBA', size=image.size, color=0)
        # watermark = Image.new('RGBA', size=(image.width, 64), color=0)
        draw = ImageDraw.Draw(watermark)
        font = get_font(60)
        tw = None
        th = None
        while True:
            tw, th = draw.textsize(text, font=font)
            if tw + 10 < image.size[0] and th + 10 < image.size[1]:
                break
            font = get_font(font.size - 2)

        draw.text(
            (image.width / 2 - tw / 2, image.height / 2 - th / 2),
            text,
            fill=(0, 0, 0, 128),
            font=font
        )

        # image.paste(watermark, box=(0, 15), mask=watermark)
        canvas.im = Image.alpha_composite(image, watermark)


def draw_bathroom(l, w, h, d, tw, th, door_size=None):
    """ Возможно следует добавить расчет "максимум целых плиток"
    :param l:
    :param w:
    :param h:
    :param d:
    :param tw:
    :param th:
    :return:
    """
    draw = Draw()

    WIDTH_HD = 1280
    HEIGHT_HD = 720

    contour_length = l/100.0 * 3.0  # 3%
    wall_del_px = contour_length * 3  # расстояние между краями схем стен
    padding_px = l/100.0 * 8.0

    # найдем ожидаемые размеры (в мм) которые может занять схема
    max_size = Size(
        width=((w+l)*2) + (wall_del_px * 3) + (padding_px * 2),
        height=h + (contour_length*2)
    )

    print(max_size)

    canvas = Canvas(
        WIDTH_HD, HEIGHT_HD,
        max_size=max_size
    )

    options = {
        'contour_out': {
                'length': canvas.to_pixels(contour_length)
            }
    }

    wall_del_px = canvas.to_pixels(wall_del_px)
    # print("wall del px=", wall_del_px)
    padding_px = canvas.to_pixels(padding_px)
    # print("padding px=", padding_px)

    draw_offset = Position(
        # WIDTH_HD/2 - canvas.to_pixels(max_size.width)/2,
        padding_px,
        HEIGHT_HD/2 - canvas.to_pixels(max_size.height)/2
    )

    # print(canvas.to_pixels(max_size.width) + padding_px)

    wall = Wall(l, h, tile=WallTilesOptions(tw, th, d, sx=None), options=options)
    draw.draw(canvas, [PositionalObject(wall, draw_offset)])
    wo = wall.get_tile_options()
    # print("Wall#1:\n\tsx={} sy={} mx={} my={}".format(wo.start_x, wo.start_y, wo.max_x, wo.max_y))

    tile_start_from_x = wall.get_tile_options().max_x
    draw_offset.x += canvas.to_pixels(wall.width) + wall_del_px
    wall = Wall(w, h, tile=WallTilesOptions(tw, th, d, sx=tile_start_from_x), options=options)
    draw.draw(canvas, [PositionalObject(wall, draw_offset)])
    wo = wall.get_tile_options()
    # print("Wall#2:\n\tsx={} sy={} mx={} my={}".format(wo.start_x, wo.start_y, wo.max_x, wo.max_y))

    tile_start_from_x = wall.get_tile_options().max_x
    draw_offset.x += canvas.to_pixels(wall.width) + wall_del_px
    if door_size is not None:
        options['door_width'] = door_size.width
        options['door_height'] = door_size.height
    wall = Wall(l, h, tile=WallTilesOptions(tw, th, d, sx=tile_start_from_x), options=options)
    draw.draw(canvas, [PositionalObject(wall, draw_offset)])
    wo = wall.get_tile_options()
    # print("Wall#3:\n\tsx={} sy={} mx={} my={}".format(wo.start_x, wo.start_y, wo.max_x, wo.max_y))

    tile_start_from_x = wall.get_tile_options().max_x
    draw_offset.x += canvas.to_pixels(wall.width) + wall_del_px
    options['door_width'] = None
    options['door_height'] = None
    wall = Wall(w, h, tile=WallTilesOptions(tw, th, d, sx=tile_start_from_x), options=options)
    draw.draw(canvas, [PositionalObject(wall, draw_offset)])
    wo = wall.get_tile_options()
    # print("Wall#4:\n\tsx={} sy={} mx={} my={}".format(wo.start_x, wo.start_y, wo.max_x, wo.max_y))

    # FIXME: little hack!!!
    real_width = draw_offset.x + canvas.to_pixels(wall.width) + padding_px
    if real_width < max_size.width:
        canvas.im = canvas.im.crop((0, 0, real_width, HEIGHT_HD))
    canvas.im.resize((WIDTH_HD, HEIGHT_HD))

    # print(real_width)

    draw.draw_wm(canvas)

    return canvas


def main():
    d = 1.5
    l = 3950
    w = 2460
    h = 2450
    tw = 400
    th = 280

    canvas = draw_bathroom(l, w, h, d, tw, th, Size(600, 2100))

    canvas.save_to_file("/home/zeez/tmp/wall.png")

    return 0


def test():
    d = 1.5
    l = 3950
    w_start = 5000
    l_start = 5000
    h_start = 5000

    w_min = 50
    l_min = 50
    h_min = 50

    tw_start = 400
    th_start = 280
    tw_min = 50
    th_min = 50

    save_path = "/home/zeez/tmp/test/"
    if not os.path.exists(save_path):
        os.system("mkdir -p %s" % save_path)
    else:
        os.system("rm {}/*".format(save_path))

    import random

    l = l_start
    w = w_start
    h = h_start
    tw = tw_start
    th = th_start

    while l >= l_min:
        while w >= w_min:
            while h >= h_min:
                while tw >= tw_min:
                    while th >= th_min:
                        print("Start calc for l={},w={},h={},d={},tw={},th={} ...".format(l, w, h, d, tw, th))
                        canvas = draw_bathroom(l, w, h, d, tw, th)
                        print("\tOK")
                        filename = "{l}-{w}-{h}_{d}_{tw}-{th}".format(l=l, w=w, h=h, d=d, tw=tw, th=th)
                        #print("Save to file {} ...".format(os.path.join(save_path, filename)))
                        #canvas.save_to_file(os.path.join(save_path, filename))
                        #print("\tSaved")

                        th -= random.randint(10, 100)

                    tw -= random.randint(10, 100)
                    th = th_start

                h -= random.randint(50, 200)
                tw = tw_start

            w -= random.randint(50, 200)
            h = h_start

        l -= random.randint(50, 200)
        w = w_start

    return 0

if __name__ == "__main__":
    # test()
    main()
