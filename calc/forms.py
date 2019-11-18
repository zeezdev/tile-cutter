from django import forms
from math import sqrt, ceil, floor
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.forms.utils import ErrorList
import os

from .algorithms import (
    check_with_delimiters,
    LAYING_METHOD_DIRECT, LAYING_METHOD_DIRECT_CENTER, LAYING_METHOD_DIAGONAL,
    draw_floor, save_image, upload_image, calc_cost, draw_walls
)


LAYING_METHODS = (
    (LAYING_METHOD_DIRECT, _("Прямой (от угла)")),
    (LAYING_METHOD_DIRECT_CENTER, _("Прямой (от центра)")),
    (LAYING_METHOD_DIAGONAL, _("Диагональный"))
)


class CalcForm(forms.Form):
    """
    :key width: Width of a room in meters.
    :key length: Length of a room in meters.
    :key tile_width: Width of the one tile (mm).
    :key tile_length: Length of the one tile (mm).
    """
    length = forms.FloatField(min_value=0.0, max_value=1000000.0, required=True, label=_("Длина помещения (m)"))
    width = forms.FloatField(min_value=0.0, max_value=1000000.0, required=True, label=_("Ширина помещения (m)"))

    tile_length = forms.IntegerField(min_value=1, max_value=10000, required=True, label=_("Длина плитки (mm)"))
    tile_width = forms.IntegerField(min_value=1, max_value=10000, required=True, label=_("Ширина плитки (mm)"))

    delimiter = forms.FloatField(min_value=0.0, max_value=10.0, required=True, label=_("Расстояние между плитками (mm)"))

    price = forms.FloatField(min_value=0.0, max_value=100000.0,
                             required=False, label=_("Стоимость одной плитки (руб)"),
                             widget=forms.NumberInput(attrs={'placeholder': _("Необязательно")}))

    reserve = forms.FloatField(min_value=0.0, max_value=100.0, label=_("Запас (%)"))

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
            raise Exception(_("Не поддерживается"))

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

    def get_data(self):
        return {
            'length': self.cleaned_data['length'],
            'width': self.cleaned_data['width'],

            'tile_length': self.cleaned_data['tile_length'],
            'tile_width': self.cleaned_data['tile_width'],

            'delimiter': self.cleaned_data['delimiter'],
            'price': self.cleaned_data['price'],
            'reserve': self.cleaned_data['reserve'],
        }

    def calc(self):
        raise NotImplementedError


class CalcFloorForm(CalcForm):
    method = forms.ChoiceField(LAYING_METHODS, required=True, label="Способ укладки")
    # TODO: start_method - 1. from center, 2. from angle

    field_order = [
        'length', 'width', 'height',
        'tile_length', 'tile_width', 'delimiter',
        'method',
        'price',
        'reserve',
    ]

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

        total_area = round((width_mm * length_mm)/10**6, 2)

        im = draw_floor(width_mm, length_mm, tile_width, tile_length, method)
        # filename = save_image(im, settings.MEDIA_ROOT)
        # img_url = os.path.join(settings.MEDIA_URL, filename)
        filename = save_image(im, '/tmp')
        img_url = upload_image(filename)
        os.remove(filename)

        return result, cost, img_url, reserve, total_area

    def get_data(self):
        data = super(CalcFloorForm, self).get_data()
        data.update({'method': self.cleaned_data['method']})
        return data


class CalcWallForm(CalcForm):

    height = forms.FloatField(min_value=0.0, max_value=1000000.0, required=True, label=_("Высота помещения (m)"))

    door_width = forms.FloatField(
        max_value=10.0, min_value=0.0, required=False,
        label=_("Ширина двери (m)"),
        widget=forms.NumberInput(attrs={'placeholder': _("Необязательно")})
    )
    door_height = forms.FloatField(
        max_value=10.0, min_value=0.0, required=False,
        label="Высота двери (m)",
        widget=forms.NumberInput(attrs={'placeholder': _("Необязательно")})
    )
    # door_position = forms.FloatField(max_value=10.0, min_value=0.0, required=False, label="Положение двери (m)")

    field_order = [
        'length', 'width', 'height',
        'tile_length', 'tile_width', 'delimiter',
        'method',
        'price',
        'reserve',
        'door_width', 'door_height'
    ]

    def __init__(self, *args, **kw):
        super(CalcWallForm, self).__init__(*args, **kw)
        self.fields['tile_width'].label = _("Высота плитки (mm)")

    def clean_door_height(self):
        data = self.cleaned_data['door_height']
        if data is not None and data > self.cleaned_data['height']:
            raise forms.ValidationError(_("Высота двери не может быть больше высоты помещения"))
        return data

    def clean_door_width(self):
        data = self.cleaned_data['door_width']
        if data is not None and data > min(self.cleaned_data['width'], self.cleaned_data['length']):
            raise forms.ValidationError(_("Ширина двери не может быть больше стен помещения"))
        return data

    def clean(self):
        cleaned_data = super(CalcWallForm, self).clean()
        if cleaned_data['door_height'] is not None and cleaned_data['door_width'] is None:
            self._errors["door_width"] = ErrorList([_("Укажите ширину двери")])

        if cleaned_data['door_width'] is not None and cleaned_data['door_height'] is None:
            self._errors["door_height"] = ErrorList([_("Укажите высоту двери")])

        return cleaned_data

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

        door_width_mm = self.cleaned_data['door_width']
        door_height_mm = self.cleaned_data['door_height']
        if door_width_mm is not None and door_height_mm is not None:
            door_width_mm *= 1000.0
            door_height_mm *= 1000.0

        perimeter_mm = (width_mm + length_mm) * 2.0
        # NOTE: наверное не стоит добавлять ширину разделителя в длину периметра
        # т.к. будет расход на пил. С другой стороны если плитку не пилят
        # а режут (плиткорезом) то расхода нет.

        # result = self._calc_direct(height_mm, perimeter_mm, tile_width, tile_length, delimiter)
        result = self._calc_direct_with_door(
            length_mm, width_mm, height_mm,
            tile_length, tile_width, delimiter,
            door_width_mm, door_height_mm
        )

        reserve = ceil(result / 100.0 * reserve_percent)

        cost = None
        if price:
            cost = calc_cost(result + reserve, price)

        total_area = round((((width_mm + length_mm) * 2) * height_mm) / 10**6, 2)

        from .drawing import draw_bathroom, Canvas, Size
        # im = draw_walls(width_mm, length_mm, height_mm, tile_length, tile_width, door_width_mm, door_height_mm)
        door_size = None
        if door_width_mm is not None and door_height_mm is not None:
            door_size = Size(door_width_mm, door_height_mm)
        canvas = draw_bathroom(length_mm, width_mm, height_mm, delimiter, tile_length, tile_width, door_size)
        # filename = save_image(canvas.im, settings.MEDIA_ROOT)
        # img_url = os.path.join(settings.MEDIA_URL, filename)
        filename = save_image(canvas.im, '/tmp')
        img_url = upload_image(filename)
        os.remove(filename)

        return result, cost, img_url, reserve, total_area

    @staticmethod
    def _calc_direct_with_door(l, w, h, tw, th, dl, door_width=None, door_height=None):  # TODO: move in to algorithms; Use direction of start.
        p = (l+w) * 2
        # NOTE: между первой плиткой и стенкой разделитель (p-dl), (h-dl)
        width_cnt = ceil((p-dl) / (tw+dl))
        height_cnt = ceil((h-dl) / (th+dl))
        tiles_in_door = 0

        if door_width and door_height:
            start_door_w = l + w + l/2 - door_width/2
            start_tile_in_door_w = ceil(start_door_w/tw) * tw  # начало первой плитки внутри двери
            tcnt_w = 0
            while start_tile_in_door_w + ((tcnt_w+1) * tw) <= start_door_w + door_width:
                tcnt_w += 1
            if tcnt_w > 0:
                tiles_in_door = int(tcnt_w * floor(door_height/th))

        return int(width_cnt * height_cnt) - tiles_in_door

    def get_data(self):
        data = super(CalcWallForm, self).get_data()
        data.update({
            'height': self.cleaned_data['height'],
            'door_width': self.cleaned_data['door_width'],
            'door_height': self.cleaned_data['door_height']
        })
        return data


class CalcTileCostForm(forms.Form):
    """Форма для нахождения стоимости одной плитки от стоимости метра квадратного
    """
    tile_length = forms.IntegerField(max_value=5000, min_value=0, required=True, label=_("Длина плитки (mm)"))
    tile_width = forms.IntegerField(max_value=5000, min_value=0, required=True, label=_("Ширина плитки (mm)"))
    price = forms.FloatField(min_value=0.0, max_value=100000.0,
                             required=True, label=_("Стоимость плитки (руб/m²)"))

    def calc(self):
        tile_area_m = self.cleaned_data['tile_length'] * self.cleaned_data['tile_width'] / 10**6
        return tile_area_m, round(tile_area_m * self.cleaned_data['price'], 2)

    def get_data(self):
        return {
            'tile_length': self.cleaned_data['tile_length'],
            'tile_width': self.cleaned_data['tile_width'],
            'price': self.cleaned_data['price']
        }
