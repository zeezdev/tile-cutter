from datetime import date

from django.conf import settings
from django.core.cache import cache

from calc.models import Result


def cutter_context(request):
    results_count = cache.get('results_count')
    if results_count is None:
        results_count = Result.objects.all().count() + settings.CUTTER_FAKE_RESULTS_NUMBER
        cache.set('results_count', results_count)

    return {
        'results_count': results_count,
        'copyright_year': date.today().strftime('%Y')
    }
