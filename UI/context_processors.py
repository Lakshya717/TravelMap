from django.urls import reverse
from .models import *

from django.urls import reverse

def site_settings(request):
    index_carousel = carousel.objects.all()
    index_features = features.objects.all()
    index_steps = step.objects.all()

    for item in list(index_carousel) + list(index_features):
        if hasattr(item, 'href') and item.href:
            try:
                item.href = reverse(item.href)
            except:
                pass

    return {
        'index_carousel': index_carousel,
        'index_features': index_features,
        'index_steps': index_steps,
    }