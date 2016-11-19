from django.shortcuts import render

from .forms import CalcFloorForm, CalcWallForm, CalcTileCostForm, LAYING_METHOD_DIRECT
from .models import Result
from .utils import get_client_ip


def floor(request):
    form = CalcFloorForm(initial={
        'method': LAYING_METHOD_DIRECT,
        'width': 3.0, 'length': 5.0,
        'tile_width': 400,
        'tile_length': 400,
        'delimiter': 1.5,
        'reserve': 5.0
    })

    context = {'form': form}

    if request.method == 'POST':
        form = CalcFloorForm(request.POST)
        context['form'] = form
        if form.is_valid():
            result, cost, image, reserve, total_area = form.calc()
            results = {
                'result': result, 'cost': cost, 'draw': image, 'reserve': reserve, 'total_area': total_area, 'total': result + reserve
            }
            context.update(results)
            result = Result(
                name="floor",
                data=form.get_data(),
                result=results,
                ip=get_client_ip(request)
            )
            result.save()

    return render(request, 'calc-floor.html', context)


def walls(request):
    form = CalcWallForm(initial={
        'width': 2.5, 'length': 3.0, 'height': 2.5,
        'tile_width': 400,
        'tile_length': 400,
        'delimiter': 1.5,
        'reserve': 5.0
    })

    context = {'form': form}

    if request.method == 'POST':
        form = CalcWallForm(request.POST)
        context['form'] = form
        if form.is_valid():
            result, cost, image, reserve, total_area = form.calc()
            results = {
                'result': result, 'cost': cost, 'draw': image, 'reserve': reserve, 'total_area': total_area,
                'total': result + reserve
            }
            context.update(results)
            result = Result(
                name="walls",
                data=form.get_data(),
                result=results,
                ip=get_client_ip(request)
            )
            result.save()

    return render(request, 'calc-walls.html', context)


def one_tile_cost(request):
    form = CalcTileCostForm(initial={
        'tile_width': 400, 'tile_length': 400, 'price': 500.0
    })

    context = {'form': form}

    if request.method == 'POST':
        form = CalcTileCostForm(request.POST)
        context['form'] = form
        if form.is_valid():
            tile_area_m, cost = form.calc()
            results = {'tile_area_m': tile_area_m, 'cost': cost}
            context.update(results)
            result = Result(
                name="one-tile-cost",
                data=form.get_data(),
                result=results,
                ip=get_client_ip(request)
            )
            result.save()

    return render(request, "calc-tile-cost.html", context)
