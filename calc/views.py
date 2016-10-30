from django.shortcuts import render

from .forms import CalcFloorForm, CalcWallForm, LAYING_METHOD_DIRECT


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
            result, cost, image, reserve = form.calc()
            context.update({
                'result': result, 'cost': cost, 'draw': image, 'reserve': reserve
            })

    return render(request, 'calc-floor.html', context)


def walls(request):
    form = CalcWallForm(initial={
        'width': 3.0, 'length': 5.0, 'height': 2.5,
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
            result, cost, image, reserve = form.calc()
            context.update({
                'result': result, 'cost': cost, 'draw': image, 'reserve': reserve
            })

    return render(request, 'calc-walls.html', context)
