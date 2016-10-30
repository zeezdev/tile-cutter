from django import forms
from math import sqrt, ceil
from django.conf import settings
import os

from .algorithms import check_with_delimiters, \
    LAYING_METHOD_DIRECT, LAYING_METHOD_DIRECT_CENTER, LAYING_METHOD_DIAGONAL, \
    draw_floor, save_image, calc_cost, draw_walls


LAYING_METHODS = (
    (LAYING_METHOD_DIRECT, "Прямой (от угла)"),
    (LAYING_METHOD_DIRECT_CENTER, "Прямой (от центра)"),
    (LAYING_METHOD_DIAGONAL, "Диагональный")
)


class CalcForm(forms.Form):
    """
    :key width: Width of a room (m^2).
    :key length: Length of a room (m^2).
    :key tile_width: Width of the one tile (mm).
    :key tile_length: Length of the one tile (mm).
    """
    length = forms.FloatField(min_value=0.0, max_value=1000000.0, required=True, label="Длина помещения (m)")
    width = forms.FloatField(min_value=0.0, max_value=1000000.0, required=True, label="Ширина помещения (m)")

    tile_width = forms.IntegerField(min_value=1, max_value=10000, required=True, label="Ширина плитки (mm)")
    tile_length = forms.IntegerField(min_value=1, max_value=10000, required=True, label="Длина плитки (mm)")

    delimiter = forms.FloatField(min_value=0.0, max_value=10.0, required=True, label="Расстояние между плитками (mm)")

    price = forms.FloatField(min_value=0.0, max_value=100000.0,
                             required=False, label="Стоимость плитки (руб)",
                             widget=forms.NumberInput(attrs={'placeholder': "Необязательно"}))

    reserve = forms.FloatField(min_value=0.0, max_value=100.0, label="Запас (%)")

    @staticmethod
    def _calc_direct(w, l, tw, tl, dl):  # TODO: move in to algorithms; Use direction of start.
        # NOTE: между первой плиткой и стенкой разделитель (w-dl)
        width_cnt = ceil((w-dl) / (tw+dl))
        length_cnt = ceil((l-dl) / (tl+dl))

        return int(width_cnt * length_cnt)

    @staticmethod
    def _calc_direct_center(w, l, tw, tl, dl):  # TODO: move in to algorithms
        twd = tw + dl
        tld = tl + dl

        half_w = (w/2) - (tw/2 + dl)
        half_l = (l/2) - (tl/2 + dl)

        cnt_w = ceil(half_w/twd) * 2 + 1
        cnt_l = ceil(half_l/tld) * 2 + 1

        return int(cnt_w * cnt_l)

    @staticmethod
    def _calc_diagonal(w, l, tw, tl, dl):  # TODO: move in to algorithms
        """
        :param w:
        :param l:
        :param tw:
        :param tl:
        :param dl: delimiter size (mm).
        :return:

        d: diagonal of tile (mm).
        """
        if tw == tl:
            d = sqrt(2) * tw
        else:
            # d = sqrt(tl**2 + tw**2)
            raise Exception("not supported")

        d05 = d / 2
        dd = sqrt(2) * dl  # delimiter diagonal
        d3 = d + dd  # tile diagonal + delimiter

        half_w = (w/2) - (d05+dd)
        half_l = (l/2) - (d05+dd)

        # количество плиток в ширину по центральному ряду (нечетные ряды)
        width_cnt = ceil(half_w/d3) * 2 + 1

        # количество плиток в ширину по четным рядам
        width_even_cnt = ceil(((w/2)-(dd/2)) / d3) * 2

        # количество плиток в длину по центральному ряду (нечетные ряды)
        length_cnt = ceil(half_l/d3) * 2 + 1

        # количество плиток в длину по четным рядам
        length_even_cnt = ceil(((l/2) - (dd/2)) / d3) * 2

        return int((width_cnt * length_cnt) + (width_even_cnt * length_even_cnt))

    def calc(self):
        raise NotImplementedError


class CalcFloorForm(CalcForm):
    method = forms.ChoiceField(LAYING_METHODS, required=True, label="Способ укладки")
    # TODO: start_method - 1. from center, 2. from angle

    def clean(self):
        cleaned_data = super(CalcFloorForm, self).clean()
        method = int(cleaned_data.get('method'))
        tile_width = cleaned_data.get('tile_width')
        tile_length = cleaned_data.get('tile_length')

        if method == LAYING_METHOD_DIAGONAL and not tile_width == tile_length:
            raise forms.ValidationError("Рассчет 'Диагонального' метода только для квадратных плиток!")

    def calc(self):
        width_mm = self.cleaned_data['width'] * 1000.0
        length_mm = self.cleaned_data['length'] * 1000.0
        method = int(self.cleaned_data['method'])
        tile_width = self.cleaned_data['tile_width']
        tile_length = self.cleaned_data['tile_length']
        delimiter = self.cleaned_data['delimiter']
        price = self.cleaned_data['price']
        reserve_percent = self.cleaned_data['reserve']

        if method == LAYING_METHOD_DIRECT:
            result = self._calc_direct(width_mm, length_mm, tile_width, tile_length, delimiter)
        elif method == LAYING_METHOD_DIRECT_CENTER:
            result = self._calc_direct_center(width_mm, length_mm, tile_width, tile_length, delimiter)
        elif method == LAYING_METHOD_DIAGONAL:
            result = self._calc_diagonal(width_mm, length_mm, tile_width, tile_length, delimiter)
        else:
            raise Exception("Unsupported method {}".format(method))

        reserve = ceil(result / 100.0 * reserve_percent)
        cost = None
        if price:
            cost = calc_cost(result + reserve, price)

        im = draw_floor(width_mm, length_mm, tile_width, tile_length, method)
        filename = save_image(im, settings.MEDIA_ROOT)
        img_url = os.path.join(settings.MEDIA_URL, filename)

        return result, cost, img_url, reserve


class CalcWallForm(CalcForm):

    height = forms.FloatField(min_value=0.0, max_value=1000000.0, required=True, label="Высота помещения (m)")

    field_order = [
        'length',
        'width',
        'height',
        'tile_width',
        'tile_length',
        'delimiter',
        'price',
        'reserve'
    ]

    def __init__(self, *args, **kw):
        super(CalcWallForm, self).__init__(*args, **kw)
        self.fields['tile_width'].label = "Высота плитки (mm)"

    def calc(self):
        width_mm = self.cleaned_data['width'] * 1000.0
        length_mm = self.cleaned_data['length'] * 1000.0
        height_mm = self.cleaned_data['height'] * 1000.0

        # method = int(self.cleaned_data['method'])

        tile_width = self.cleaned_data['tile_width']
        tile_length = self.cleaned_data['tile_length']
        delimiter = self.cleaned_data['delimiter']
        price = self.cleaned_data['price']
        reserve_percent = self.cleaned_data['reserve']

        perimeter_mm = (width_mm + length_mm) * 2.0
        # NOTE: наверное не стоит добавлять ширину разделителя в длину периметра
        # т.к. будет расход на пил. С другой стороны если плитку не пилять
        # а режут (плиткорезом) то расхода нет.

        result = self._calc_direct(height_mm, perimeter_mm, tile_width, tile_length, delimiter)
        reserve = ceil(result / 100.0 * reserve_percent)

        cost = None
        if price:
            cost = calc_cost(result + reserve, price)

        im = draw_walls(width_mm, length_mm, height_mm, tile_length, tile_width)
        filename = save_image(im, settings.MEDIA_ROOT)
        img_url = os.path.join(settings.MEDIA_URL, filename)

        return result, cost, img_url, reserve





