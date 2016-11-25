#from django.contrib.sessions.middleware import SessionMiddleware

from django.conf import settings
from calc.models import Result


def cutter_context(request):
    context_data = dict()
    context_data['results_count'] = request.results_count = int(
            Result.objects.all().count() + settings.CUTTER_FAKE_RESULTS_NUMBER)
    return context_data
