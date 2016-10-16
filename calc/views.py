from django.shortcuts import render

from .forms import CalcFloorForm, CalcWallForm, LAYING_METHOD_DIRECT


def floor(request):
    form = CalcFloorForm(initial={
        'method': LAYING_METHOD_DIRECT,
        'width': 5.0, 'length': 5.0,
        'tile_width': 400,
        'tile_length': 400,
        'delimiter': 1.5
    })

    result = None
    cost = None
    image = None

    if request.method == 'POST':
        form = CalcFloorForm(request.POST)
        if form.is_valid():
            result, cost, image = form.calc()
        # else:
        #     result = "Ошибка"

    return render(request, 'calc-floor.html', {'form': form, 'result': result, 'cost': cost, 'draw': image})


def walls(request):
    form = CalcWallForm(initial={
        'width': 5.0, 'length': 5.0, 'height': 2.5,
        'tile_width': 400,
        'tile_length': 400,
        'delimiter': 1.5
    })

    result = None
    cost = None
    image = None

    if request.method == 'POST':
        form = CalcWallForm(request.POST)
        if form.is_valid():
            result, cost, image = form.calc()
        # else:
        #     result = "Ошибка"

    return render(request, 'calc-walls.html', {'form': form, 'result': result, 'cost': cost, 'draw': image})
