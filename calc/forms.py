from django import forms
from math import sqrt, ceil
from django.conf import settings
import os

from .algorithms import check_with_delimiters, \
    LAYING_METHOD_DIRECT, LAYING_METHOD_DIRECT_CENTER, LAYING_METHOD_DIAGONAL, draw_floor, save_image


LAYING_METHODS = (
    (LAYING_METHOD_DIRECT, "Прямой (от угла)"),
    (LAYING_METHOD_DIRECT_CENTER, "Прямой (от центра)"),
    (LAYING_METHOD_DIAGONAL, "Диагональный")
)


class CalcFloorForm(forms.Form):
    """
    :key width: Width of a room (m^2).
    :key length: Length of a room (m^2).
    """

    method = forms.ChoiceField(LAYING_METHODS, required=True, label="Способ укладки")
    # TODO: start_method - 1. from center, 2. from angle

    width = forms.FloatField(min_value=0.0, max_value=1000000.0, required=True, label="Ширина помещения (m²)")
    length = forms.FloatField(min_value=0.0, max_value=1000000.0, required=True, label="Длина помещения (m²)")

    tile_width = forms.IntegerField(min_value=1, max_value=10000, required=True, label="Ширина плитки (мм)")
    tile_length = forms.IntegerField(min_value=1, max_value=10000, required=True, label="Длина плитки (мм)")

    delimiter = forms.FloatField(min_value=0.0, max_value=10.0, required=True, label="Расстояние между плитками (мм)")

    price = forms.FloatField(min_value=0.0, max_value=100000.0,
                             required=False, label="Стоимость плитки (руб)",
                             widget=forms.NumberInput(attrs={'placeholder': "Необязательно"}))

    def clean(self):
        cleaned_data = super(CalcFloorForm, self).clean()
        method = int(cleaned_data.get('method'))
        tile_width = cleaned_data.get('tile_width')
        tile_length = cleaned_data.get('tile_length')

        if method == LAYING_METHOD_DIAGONAL and not tile_width == tile_length:
            raise forms.ValidationError("Рассчет 'Диагонального' метода только для квадратных плиток!")

    @staticmethod
    def _calc_direct(w, l, tw, tl, dl):
        tile_width_cnt = ceil(w / tw)
        tile_length_cnt = ceil(l / tl)

        # уточнение с межплиточным расстоянием
        # dl_w = dl * (tile_width_cnt-1)
        # dl_l = dl * (tile_length_cnt-1)
        #
        # if (tile_width_cnt * tw) + dl_w - w >= tw:
        #     tile_width_cnt -= 1
        #
        # if (tile_length_cnt * tl) + dl_l - l >= tl:
        #     tile_length_cnt -= 1
        tile_width_cnt = check_with_delimiters(w, tw, dl, tile_width_cnt)
        tile_length_cnt = check_with_delimiters(l, tl, dl, tile_length_cnt)

        return int(tile_width_cnt * tile_length_cnt)

    @staticmethod
    def _calc_direct_center(w, l, tw, tl, dl):
        tw05 = tw/2
        tile_width_cnt = ceil(((w/2)-tw05) / tw)
        tile_width_cnt *= 2
        tile_width_cnt += 1

        tl05 = tl/2
        tile_length_cnt = ceil(((l/2)-tl05) / tl)
        tile_length_cnt *= 2
        tile_length_cnt += 1

        # уточнение с межплиточным расстоянием
        # dl_w = dl * (tile_width_cnt-1)
        # dl_l = dl * (tile_length_cnt-1)
        #
        # if (tile_width_cnt * tw) + dl_w - w >= tw:
        #     tile_width_cnt -= 1
        #
        # if (tile_length_cnt * tl) + dl_l - l >= tl:
        #     tile_length_cnt -= 1
        tile_width_cnt = check_with_delimiters(w, tw, dl, tile_width_cnt)
        tile_length_cnt = check_with_delimiters(l, tl, dl, tile_length_cnt)

        return int(tile_width_cnt * tile_length_cnt)

    @staticmethod
    def _calc_diagonal(w, l, tw, tl, dl):
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
            d = sqrt(tl**2 + tw**2)

        d05 = d / 2
        dd = sqrt(2) * d  # delimiter diagonal

        # количество плиток в ширину по центральному ряду (нечетные ряды)
        tile_width_cnt = ceil(((w/2) - d05) / d)
        tile_width_cnt *= 2
        tile_width_cnt += 1  # center
        tile_width_cnt = check_with_delimiters(w, d, dd, tile_width_cnt)

        # количество плиток в ширину по четным рядам
        tile_width_even_cnt = ceil((w/2) / d)
        tile_width_even_cnt *= 2
        tile_width_even_cnt = check_with_delimiters(w, d, dd, tile_width_even_cnt)

        # количество плиток в длину по центральному ряду (нечетные ряды)
        tile_length_cnt = ceil(((l/2) - d05) / d)
        tile_length_cnt *= 2
        tile_length_cnt += 1
        tile_length_cnt = check_with_delimiters(l, d, dd, tile_length_cnt)

        # количество плиток в длину по четным рядам
        tile_length_even_cnt = ceil((l/2) / d)
        tile_length_even_cnt *= 2
        tile_length_even_cnt = check_with_delimiters(l, d, dd, tile_length_even_cnt)

        return int((tile_width_cnt * tile_length_cnt) + (tile_width_even_cnt * tile_length_even_cnt))

    def calc(self):
        width_mm = self.cleaned_data['width'] * 1000.0
        length_mm = self.cleaned_data['length'] * 1000.0
        method = int(self.cleaned_data['method'])
        tile_width = self.cleaned_data['tile_width']
        tile_length = self.cleaned_data['tile_length']
        delimiter = self.cleaned_data['delimiter']
        price = self.cleaned_data['price']

        if method == LAYING_METHOD_DIRECT:
            result = CalcFloorForm._calc_direct(width_mm, length_mm, tile_width, tile_length, delimiter)
        elif method == LAYING_METHOD_DIRECT_CENTER:
            result = CalcFloorForm._calc_direct_center(width_mm, length_mm, tile_width, tile_length, delimiter)
        elif method == LAYING_METHOD_DIAGONAL:
            result = CalcFloorForm._calc_diagonal(width_mm, length_mm, tile_width, tile_length, delimiter)
        else:
            raise Exception("Unsupported method {}".format(method))

        cost = None
        if price:
            cost = round(price * result, 2)

        im = draw_floor(width_mm, length_mm, tile_width, tile_length, method)
        filename = save_image(im, "/home/zeez/tmp/")
        img_url = os.path.join(settings.MEDIA_URL, filename)

        return result, cost, img_url





