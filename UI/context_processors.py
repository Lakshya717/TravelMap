from .models import *

def site_settings(request):
    return {
        'index_carousel': carousel.objects.all(),
        'index_features': features.objects.all(),
        'index_steps': step.objects.all(),
    }
