from django.conf import settings


def global_settings(request):
    # return any necessary values
    return {
        'ENVIRONMENT': settings.ENVIRONMENT
    }